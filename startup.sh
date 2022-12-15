#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py inital_user
python manage.py runserver 0.0.0.0:8000