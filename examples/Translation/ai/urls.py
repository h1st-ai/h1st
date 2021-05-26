from django.urls import path

from .views import TranslationModelAPIView


urlpatterns = [
    path('execute/', TranslationModelAPIView.as_view())
]
