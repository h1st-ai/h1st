"""
WSGI config for a project

It exposes the WSGI callable as a module-level variable named ``application``

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi
"""

from django.core.wsgi import get_wsgi_application

import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
