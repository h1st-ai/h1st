# H1st customizations
from django.conf.urls import url
from .settings import INSTALLED_APPS
from django.urls import path, include
from rest_framework import routers
import importlib


INSTALLED_APPS.append("rest_framework")
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"]
}


def make_url_patterns(input, urls=[]):
    for uri, klass in input.items():
        urls.append(path(uri, klass().handle_request))
    return urls


# Has web UI?
exists = importlib.util.find_spec("ui.web_urls")
if exists is not None:
    from ui.web_urls import WEB_URLS
    try:
        urlpatterns = make_url_patterns(WEB_URLS, urlpatterns)
    except:
        urlpatterns = make_url_patterns(WEB_URLS)

# Has REST UI?
exists = importlib.util.find_spec("ui.rest_urls")
if exists is not None:
    from ui.rest_urls import REST_URLS
    try:
        urlpatterns = make_url_patterns(REST_URLS, urlpatterns)
    except:
        urlpatterns = make_url_patterns(REST_URLS)

    urlpatterns.append(path("api-auth/", include("rest_framework.urls")))