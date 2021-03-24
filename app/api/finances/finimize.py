import os
import datetime
from gql import gql
from gql.transport.exceptions import TransportQueryError
from .throttler import Limit, FinimizeThrottler


class Finimize(FinimizeThrottler):

    def __init__(self):
        self.url = "https://app.finimize.com/api/graphql/"
        self.headers = {
            "x-app-version": "2.0.2",
            "Accept-Encoding": "gzip",
            "cookie": "csrftoken=qd5DjEr1jRqrxLsSa0idPYyY4h75mi2AhUdmxAuy3fuwZH7xxNeUcT2tVPisAHkM",
            "authorization": "Token ecc4de1d89b4d082770482b98bcc104594957fe908d560ad351189551a9faa4e",
            "User-Agent": "okhttp/3.12.1",
            "Content-Type": "application/json"
        }

        queries_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finimize_queries")
        with open(os.path.join(queries_dir, "content_first.graphql"), "r") as file:
            self.first_query = gql(file.read())
        with open(os.path.join(queries_dir, "content_pagination.graphql"), "r") as file:
            self.pagination_query = gql(file.read())
        with open(os.path.join(queries_dir, "single_content_piece.graphql"), "r") as file:
            self.content_piece_query = gql(file.read())

        self.content_types = ["DAILY_BRIEF", "INSIGHT", "OTHER"]

        super(Finimize, self).__init__([
            Limit(30, 60, 1, "fm:short"), Limit(1000, 86400, 1800, "fm:long")
        ], self.url, self.headers)

    def clean_chapters(self, response):
        for chapter in range(len(response["chapters"])):
            chapter["_id"] = chapter.pop("id")
            del response["chapters"][chapter]["audioDuration"]
            del response["chapters"][chapter]["trackingTitle"]
        response["chapters"][chapter] = self._clean_blocks(response["chapters"][chapter])
        return response

    def _clean_blocks(self, response):
        rm_blocks = [i for i in range(len(response["blocks"])) if response["blocks"][i]["__typename"] == "ImageBlock"]
        for block_idx in rm_blocks[::-1]:
            del response["blocks"][block_idx]
        return response

    async def get_ids(self, content_type: str, after: str = None):
        params = {
            "count": 10,
            "after": after,
            "contentTypes": [content_type],
            "tagName": None
        }

        if content_type is None:
            query = self.first_query
        else:
            query = self.pagination_query

        try:
            response = await self.make_request(query, variable_values=params)
        except TransportQueryError:
            return None, None

        data = response["viewer"]["me"]["contentPieces"]["edges"]
        ids = [datum["node"]["id"] for datum in data]
        cursors = [datum["cursor"] for datum in data]

        return ids, cursors

    async def get_single(self, _id: str):
        params = {
            "contentPieceId": _id
        }

        try:
            response = await self.make_request(self.content_piece_query, variable_values=params)
        except TransportQueryError:
            return None, None
        response = response["viewer"]["me"]["contentPiece"]

        response["_id"] = response.pop("id")
        response["dateUpdatedDisplay"] = datetime.datetime.fromisoformat(response["dateUpdatedDisplay"])

        if "headerImage" in response:
            del response["headerImage"]
        if "trackingTitle" in response:
            del response["trackingTitle"]
        if "audioUrl" in response:
            del response["audioUrl"]
        if "readingTime" in response:
            del response["readingTime"]

        response = self._clean_blocks(response)

        related_contents = response.pop("relatedContentPieces")
        related_ids = [related["id"] for related in related_contents]
        for related in related_contents:
            related["_id"] = related.pop("id")
            del related["headerImage"]

        return response, related_ids
