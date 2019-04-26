while ! wget $DB_HOST:3306 -q; do
    sleep 1
done
pipenv run python manage.py runserver 0.0.0.0:8000
