import os 
import os.path
import uuid
import json

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
        print(model_type, model_id)

        if model_type == "img_classifer":
            # try:
            file = request.FILES['file']
            # file_name, file_id = self.handle_uploaded_file(file)
            
            # if uploaded_file.size > 200 * 1024:
            #     return "Sorry, we accept only images with size <= 200KB"
            image_data = file.read()

            # retrieve model
            model = AIModel.objects.get(model_id=model_id);
            spec = model.config

            print(type(spec))

            return Response({
                "status": "OK",
                "result": self.execute(model_id, input_data=image_data, input_type='image', spec=spec)
            })
            # except Exception as ex:
            #     print(ex)
            #     # TODO handle error here
            #     return Response({
            #         "status": "BAD_REQUEST",
            #     })

        # not supported
        return Response({
            'status': 'NOT_SUPPORTED',
        })

    def execute(self, model_id, input_data, input_type, spec):
        model_info = ModelManager.get_model_config(model_id)
        step = H1ModelStep(model_id, model_info.model_platform, model_info.model_path)
        return ModelExecutor.execute(step, input_data, input_type, spec)