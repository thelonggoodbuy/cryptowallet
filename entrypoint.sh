#!/bin/sh


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgress..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done

    echo "Postgres starter"
fi

echo "**************************************"

alembic -c ./db_config/alembic.ini revision --autogenerate -m "initial_migration"
alembic -c ./db_config/alembic.ini revision upgrade head
# python manage.py makemigrations
# python manage.py migrate
# python manage.py users_initial_script
# echo "yes" | python manage.py collectstatic
# echo "**************************************"

echo "(----------------DB work!----------------)"

exec "$@"
