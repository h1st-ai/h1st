from django.urls import path
from h1st_api import views
from h1st_api.controllers.upload import Upload
from h1st_api.controllers.application import Application

urlpatterns = [
    path('', views.default),
    path('upload/', Upload.as_view()),
    path('app/<path:model_id>/', Application.as_view())
]

