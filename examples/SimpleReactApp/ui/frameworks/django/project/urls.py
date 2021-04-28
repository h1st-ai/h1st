# H1st customizations
from django.conf.urls import url
from django.urls import path, include
import importlib


def add_url_patterns(input, urls=[]):
    for uri, obj in input.items():
        if callable(getattr(obj, "handle_request", None)):
            urls.append(path(uri, obj().handle_request))

        elif hasattr(obj, '__call__'):
            urls.append(path(uri, obj))

    return urls


# Has web UI?
exists = importlib.util.find_spec("ui.web_urls")
if exists is not None:
    from ui.web_urls import WEB_URLS
    try:
        urlpatterns = add_url_patterns(WEB_URLS, urlpatterns)
    except:
        urlpatterns = add_url_patterns(WEB_URLS)


# Has REST UI?
exists = importlib.util.find_spec("ui.rest_urls")
if exists is not None:
    from ui.rest_urls import REST_URLS
    try:
        urlpatterns = add_url_patterns(REST_URLS, urlpatterns)
    except:
        urlpatterns = add_url_patterns(REST_URLS)

    # Also make /api-auth/ available (?)
    urlpatterns.append(path("api-auth/", include("rest_framework.urls")))