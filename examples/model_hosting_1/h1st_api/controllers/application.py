from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict

import os 
import os.path
import uuid
import json


from .model_manager import TensorFlowModelManager

# from ui.frameworks.django.app.models import AIModel
# from .models import AIModel
from h1st_api.models import AIModel

class Application(APIView):

    def get(self, request, model_id):
        # model_id = kwargs.get('model_id')
        print(model_id)

        model = AIModel.objects.get(pk=model_id);

        return Response({
            'status': 'OK',
            'model': model_to_dict(model)
        })