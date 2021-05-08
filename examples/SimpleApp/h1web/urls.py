from django.urls import path
from h1web import views

urlpatterns = [
    path("", views.default),
]
