from django.urls import path
from h1st_api import views
from h1st_api.controllers.upload import Upload
from h1st_api.controllers.application import Application
from h1st_api.controllers.execution import Execution

urlpatterns = [
    path('', views.default),
    path('upload/', Upload.as_view()),
    path('app/<path:model_id>/execute/<path:model_type>/', Application.as_view()),
    path('app/<path:model_id>/', Application.as_view()),
]

