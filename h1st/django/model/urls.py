from django.urls.conf import include, path

from rest_framework.routers import DefaultRouter

from .api.rest.views import H1stModelViewSet, ModelExecAPIView, TestAPIView
from .views import model_exec_on_json_input_data


CORE_REST_API_ROUTER = DefaultRouter(trailing_slash=False)

CORE_REST_API_ROUTER.register(
    prefix='',
    viewset=H1stModelViewSet,
    basename=None)


urlpatterns = [
    path(route='',
         view=include(CORE_REST_API_ROUTER.urls)),

    path(route='exec/',
         view=ModelExecAPIView.as_view()),

    path(route='<str:model_uuid>/<str:json_input_data>/',
         view=model_exec_on_json_input_data),

    path(route='test/',
         view=TestAPIView.as_view())
]
