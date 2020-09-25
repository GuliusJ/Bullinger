#!/bin/bash
#db_delete.sh

# DANGEROUS !

:'
rm -rf migrations

rm app.db
touch app.db

flask db init
flask db migrate -m "new empty database"
flask db upgrade
'