import os 
import os.path
import uuid
import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict

from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from h1st_api.models import AIModel

from h1st_api.controllers.mocked.model_step import H1ModelStep
from .model_executor import ModelExecutor
from .model_manager import ModelManager

@permission_classes([AllowAny])
class Application(APIView):

    def get(self, request, model_id):
        model = AIModel.objects.get(model_id=model_id);

        return Response({
            'status': 'OK',
            'model': model_to_dict(model)
        })
    
    def post(self, request, model_id, model_type):
        if model_type == "img_classifer":
            try:
                file = request.FILES['file']

                if file.size > 10 * 1024 * 1024:
                    return Response({
                        "status": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        "message": "The uploaded photo exceeds maximum file size."
                    }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

            except Exception as ex:
                print(ex)

                return Response({
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Internal server error"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            image_data = file.read()

            try:
                # retrieve model
                model = AIModel.objects.get(model_id=model_id);

                print("Model retrieve",  model)

                return Response({
                    "status": "OK",
                    "result": self.execute(model_id, input_data=image_data, input_type='image', spec=model.config)
                })
            except Exception as ex:
                print(ex)
                # TODO handle error here
                return Response({
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Internal server error"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # not supported
        return Response({
            'status': status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            'message': 'Unsupported type'
        }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def execute(self, model_id, input_data, input_type, spec):
        model_info = ModelManager.get_model_config(model_id)
        step = H1ModelStep(model_id, model_info.model_platform, model_info.model_path)
        return ModelExecutor.execute(step, input_data, input_type, spec)