"""
ASGI config for a project

It exposes the ASGI callable as a module-level variable named ``application``

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi
"""

from django.core.asgi import get_asgi_application

import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_asgi_application()
