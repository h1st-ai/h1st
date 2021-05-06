from django.urls import path
from h1st_api import views

urlpatterns = [
    path('', views.default),
]

