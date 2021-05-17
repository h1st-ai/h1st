#!/bin/bash

cd /app
python manage.py migrate 
gunicorn -b :8000 model_hosting_1.wsgi --timeout 120

