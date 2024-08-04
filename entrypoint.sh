#!/bin/sh


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgress..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done

    echo "Postgres starter"
fi

echo "**********ALEMBIC***HEAD****************************"

alembic -c ./db_config/alembic.ini upgrade head
chmod -R +rx front
python3 management/initial_script.py

echo "*****END***ALEMBIC***HEAD***************************"

echo "(----------------DB work!----------------)"

exec "$@"
