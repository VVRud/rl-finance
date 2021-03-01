#! /bin/bash

if [ "$MONGO_INITDB_USERNAME" ] && [ "$MONGO_INITDB_PASSWORD" ]; then
"${mongo[@]}" "$MONGO_INITDB_DATABASE" <<-EOJS
    db.createUser({
        user: $(_js_escape "$MONGO_INITDB_USERNAME"),
        pwd: $(_js_escape "$MONGO_INITDB_PASSWORD"),
        roles: [ { role: 'readWrite', db: $(_js_escape "$MONGO_INITDB_DATABASE") } ]
    })
EOJS
fi
