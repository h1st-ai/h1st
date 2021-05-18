#!/bin/bash

cd /app
python manage.py migrate 
gunicorn -b :8000 --workers=100 --timeout 120 model_hosting_1.wsgi:application

