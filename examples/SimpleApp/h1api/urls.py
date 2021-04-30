from django.urls import path
from h1api import views

urlpatterns = [
    path("", views.default),
]
