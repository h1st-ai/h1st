from django.urls.conf import include, path

from .data import urls as data_urls
from .model import urls as model_urls
from .trust import urls as trust_urls


urlpatterns = [
    path(route='data/',
         view=include(data_urls)),

    path(route='models/',
         view=include(model_urls)),
    path(route='model/',
         view=include(model_urls)),
    path(route='workflows/',
         view=include(model_urls)),
    path(route='workflow/',
         view=include(model_urls)),

    path(route='trust/',
         view=include(trust_urls))
]
