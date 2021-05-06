from django.urls import path
from h1st_react import views

urlpatterns = [
    path('', views.default),
]

