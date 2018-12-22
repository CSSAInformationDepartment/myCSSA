#!/bin/bash

TIMEOUT=15
QUIET=0

SQLCONNECTED='FALSE'

>&2 echo "Checking Postgres"

until [ $SQLCONNECTED = 'TRUE' ] 
do
    SERVER=db
    PORT=5432
    `nc -z $SERVER $PORT`
    result1=$?
    if [  "$result1" != 0 ]; then
      >&2 echo "Postgres is unavailable - sleeping"
    else
        >&2 echo "Postgres is up - Loading Web Service Engine..."
        SQLCONNECTED='TRUE'
    fi
    sleep 1
done

python3 manage.py makemigrations

python3 manage.py migrate

>&2 echo "Web Services is now ready to start"

exec python3 manage.py runserver 0.0.0.0:8000

