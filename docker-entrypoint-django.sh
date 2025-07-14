#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Compiling translations..."
python manage.py compilemessages

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Populating data..."
python manage.py clear_db
python ./data_populator/delete_sectors_and_reports.py
python ./data_populator/import_reports.py
python ./data_populator/import_cyber_security_data.py
python manage.py populate_db

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000