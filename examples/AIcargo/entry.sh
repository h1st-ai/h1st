#!/bin/bash

cd /app
python manage.py migrate 
# gunicorn -b :8000 --workers=100 --timeout 120 model_hosting_1.wsgi:application
gunicorn -b :8000  --worker-class=gevent --worker-connections=1000 --workers=80 --timeout 120 model_hosting_1.wsgi:application
