from django.urls import path
from h1st_api import views
from h1st_api.controllers.upload import Upload

urlpatterns = [
    path('', views.default),
    path('upload/', Upload.as_view())
]

