from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from .models.google_cloud import GoogleLanguageTranslationModel


@permission_classes([AllowAny])
class TranslationModelAPIView(APIView):
    def post(self, request, *args, **kwargs):
        model = GoogleLanguageTranslationModel()
        result = model.predict(request.data, target='fr')
        return Response(result)
