from django.urls.conf import include, path

from rest_framework.routers import DefaultRouter

from .api.rest.views import DataSetViewSet, DataQueryAPIView


CORE_REST_API_ROUTER = DefaultRouter(trailing_slash=False)

CORE_REST_API_ROUTER.register(
    prefix='',
    viewset=DataSetViewSet,
    basename=None)


urlpatterns = [
    path(route='',
         view=include(CORE_REST_API_ROUTER.urls)),

    path(route='query/',
         view=DataQueryAPIView.as_view())
]
