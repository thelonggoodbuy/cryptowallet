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
python3 management/initial_script.py
# python db_config/management/db_initialisation.py


# alembic_status=$?

# if [ $alembic_status -ne 0 ]; then
#     echo "Alembic migration failed"
#     exit 1
# fi

echo "*****END***ALEMBIC***HEAD***************************"

# python manage.py makemigrations
# python manage.py migrate
# python manage.py users_initial_script
# echo "yes" | python manage.py collectstatic
# echo "**************************************"

echo "(----------------DB work!----------------)"

exec "$@"
