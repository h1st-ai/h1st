from .mock_framework import H1StepWithWebUI
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import zipfile36 as zipfile
import os 
import os.path
import uuid
import json
from zipfile import ZipFile

from .model_manager import TensorFlowModelManager

# from ui.frameworks.django.app.models import AIModel
from .models import AIModel

class Upload(H1StepWithWebUI):
    def __init__(self):
        self.model_extract_path = "models"
        self.model_config_path = "models/models.config"

    @csrf_exempt
    def handle_request(self, req):
        if (req.method == 'GET'):
            return self.handle_get(req)
        elif (req.method == 'POST'):
            return self.handle_post(req)
        elif (req.method == 'PUT'):
            return self.handle_post(req)
        elif (req.method == 'DELETE'):
            return self.handle_post(req)
        else:
            return self.handle_default(req)

    def handle_get(self, req):
        user = "mocked_user"
        models = list(AIModel.objects.filter().values())

        # add paging
        return JsonResponse({
            'status': 'OK',
            'result': models
        })
    
    def handle_post(self, req):
        try:
            file = req.FILES['file']
            file_name, file_id = self.handle_uploaded_file(file)
            
            return JsonResponse({
                    "status": "OK",
                    "id": file_id
                }) 

        except:
            data = json.loads(req.body)
            name = data['name']
            description = data['description']
            model_input = data['input']
            model_output = data['output']
            file_name = data['uploadedFile']
            creator="mocked_user"

            #deploy the model first
            file_path = "uploaded/" + file_name
            dir_name = file_name.split('.')[0]
            deploy_result = self.deploy_model(dir_name, file_path)
            
            if deploy_result is False:
                return JsonResponse({
                    "status": "DEPLOYMENT_ERROR"
                })
                

            #save to database
            m = AIModel(
                name=name,
                description=description,
                model_input=model_input,
                model_output=model_output,
                file_name=file_name,
                creator=creator
            )

            # persist
            m.save()

            return JsonResponse({
                "status": "OK",
                "result": {
                    'id': m.id,
                    'name': name,
                    'description': description,
                    'input': model_input,
                    'output': model_output,
                    'created_at': m.created_at,
                    'updated_at': m.updated_at,
                    'creator': 'mocked_user'
                }
            }) 

    def create_model_config(self):
        os.mkdir(self.model_extract_path)
        with open(self.model_config_path, 'a') as out:
            out.write(f'model_config_list {{}}' + '\n')
    
    def deploy_model(self, file_name, file_path):
        # check to see if the directory exist
        if not os.path.exists(self.model_config_path):
            self.create_model_config()

        try:
            with ZipFile(file_path, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall(path='{}/{}'.format(self.model_extract_path, file_name))
            
            # consider deleting the uploaded file at this point
            TensorFlowModelManager.register_new_model(conf_filepath="model_repo/tensorflow_models/models.config", name=file_name, base_path="/models/{}/".format(file_name))
            return True

        except Exception as ex:
            print(type(ex))    # the exception
            print(ex.args)     # arguments stored in .args
            print(ex)          # __str__ allows args to be printed directly,

            return False
            
    def handle_uploaded_file(self, f):
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(str(f))[1]

        qualified_name = "uploaded/" + file_id + ext

        with open(qualified_name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_id, file_id + ext