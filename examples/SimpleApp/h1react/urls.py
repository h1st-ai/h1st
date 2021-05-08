from django.urls import path
from h1react import views

urlpatterns = [
    path("", views.default),
]
