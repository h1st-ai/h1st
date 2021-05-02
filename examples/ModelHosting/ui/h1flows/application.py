from .mock_framework import H1StepWithWebUI
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.core import serializers
import zipfile36 as zipfile
import os 
import os.path
import uuid
import json
from zipfile import ZipFile


from .model_manager import TensorFlowModelManager

# from ui.frameworks.django.app.models import AIModel
from .models import AIModel

class Application(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req, *args, **kwargs):
        if (req.method == 'GET'):
            return self.handle_get(req, *args, **kwargs)
        elif (req.method == 'POST'):
            return self.handle_post(req, *args, **kwargs)
        elif (req.method == 'PUT'):
            return self.handle_post(req, *args, **kwargs)
        elif (req.method == 'DELETE'):
            return self.handle_post(req, *args, **kwargs)
        else:
            return self.handle_default(req, *args, **kwargs)

    def handle_get(self, req, *args, **kwargs):
        model_id = kwargs.get('model_id')
        print(model_id)

        model = AIModel.objects.get(pk=model_id);

        return JsonResponse({
            'status': 'OK',
            'model': model_to_dict(model)
        })