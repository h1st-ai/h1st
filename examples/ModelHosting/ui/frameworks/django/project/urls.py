# H1st customizations
from ui.h1flow_urls import H1FLOW_URLS
from django.urls import path, include

def make_url_patterns(input):
    urls = [
        path('api-auth/', include('rest_framework.urls'))
    ]

    for uri, klass in input.items():
        urls.append(path(uri, klass().handle_request))

    return urls

urlpatterns = make_url_patterns(H1FLOW_URLS)

