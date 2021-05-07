from rest_framework.views import APIView
from rest_framework.response import Response

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
from h1st_api.models import ModelClass

# from ui.frameworks.django.app.models import AIModel
from h1st_api.models import AIModel

class Upload(APIView):
    def __init__(self):
        super().__init__()
        self.UPLOAD_PATH = "uploaded"
        self.MODEL_EXT_PATH = "model_repo"
        self.TF_PATH = "{}/tensorflow_models".format(self.MODEL_EXT_PATH)
        self.TF_MODEL_CONFIG = "{}/models.config".format(self.TF_PATH)
        self.TF_MODEL_IO_FILE = "model-io.json"
        
    # @csrf_exempt
    # def handle_request(self, req):
    #     if (req.method == 'GET'):
    #         return self.handle_get(req)
    #     elif (req.method == 'POST'):
    #         return self.handle_post(req)
    #     elif (req.method == 'PUT'):
    #         return self.handle_post(req)
    #     elif (req.method == 'DELETE'):
    #         return self.handle_post(req)
    #     else:
    #         return self.handle_default(req)

    def get(self, request, format=None):
        """
        Return a list of applications for the current user
        """
        user = "mocked_user"
        models = list(AIModel.objects.filter().values())

        # add paging
        # return JsonResponse({
        #     'status': 'OK',
        #     'result': models
        # })

        # usernames = [user.username for user in User.objects.all()]
        return Response({
            'status': 'OK',
            'result': models
        })

    # def handle_get(self, req):
    #     user = "mocked_user"
    #     models = list(AIModel.objects.filter().values())

    #     # add paging
    #     return JsonResponse({
    #         'status': 'OK',
    #         'result': models
    #     })
    
    def post(self, request, format=None):
        try:
            file = request.FILES['file']
            file_name, file_id = self.handle_uploaded_file(file)
            
            return JsonResponse({
                "status": "OK",
                "id": file_id
            })
        except:
            # print(request.data)
            # data = json.loads(request.data)
            data = request.data
            name = data['name']
            description = data['description']
            model_input = data['input']
            model_output = data['output']
            file_name = data['uploadedFile']
            type = data['type']
            creator="mocked_user"

            if type == ModelClass.TF:
                #deploy the model first
                file_path = "{}/{}".format(self.UPLOAD_PATH, file_name)
                dir_name = file_name.split('.')[0]
                deploy_result, config_data = self.deploy_tf_model(dir_name, file_path, model_type=type)
                
                if deploy_result is False:
                    return JsonResponse({
                        "status": "DEPLOYMENT_ERROR"
                    })
                

            #save to database
            m = AIModel(
                model_id=dir_name,
                name=name,
                type=type,
                description=description,
                input=model_input,
                output=model_output,
                file_name=file_name,
                config=config_data,
                creator=creator
            )

            # persist
            m.save()

            return JsonResponse({
                "status": "OK",
                "result": {
                    'id': m.id,
                    'model_id':dir_name,
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
        os.mkdir(self.MODEL_EXT_PATH)
        os.mkdir(self.TF_PATH)
        with open(self.TF_MODEL_CONFIG, 'a') as out:
            out.write(f'model_config_list {{}}' + '\n')
    
    def deploy_tf_model(self, file_name, file_path, model_type = ModelClass.TF):
        if model_type == ModelClass.TF :
            # check to see if the directory exist
            if not os.path.exists(self.MODEL_EXT_PATH):
                self.create_model_config()

            try:
                with ZipFile(file_path, 'r') as Z:
                    # destination = '{}/{}'.format(self.TF_PATH, file_name)

                    # for elem in Z.namelist() :
                    #     Z.extract(elem, destination)
                    # Extract all the contents of zip file in current directory
                    Z.extractall(path='{}/{}'.format(self.TF_PATH, file_name))
                
                # consider deleting the uploaded file at this point
                TensorFlowModelManager.register_new_model(conf_filepath=self.TF_MODEL_CONFIG, name=file_name, base_path="/models/{}/".format(file_name))
                
                # read model.io.json
                config_data = self.handle_modelio_json(path='{}/{}/{}'.format(self.TF_PATH, file_name, self.TF_MODEL_IO_FILE))

                return True, config_data

            except Exception as ex:
                print(type(ex))    # the exception
                print(ex.args)     # arguments stored in .args
                print(ex)          # __str__ allows args to be printed directly,

                return False
        
        return True
    
    def handle_modelio_json(self, path):
        f = open(path,)
  
        # returns JSON object as 
        # a dictionary
        data = json.load(f)
        
        # Closing file
        f.close()

        return data
            
    def handle_uploaded_file(self, f):
        if not os.path.exists(self.UPLOAD_PATH):
            os.mkdir(self.UPLOAD_PATH)

        file_id = str(uuid.uuid4())
        ext = os.path.splitext(str(f))[1]

        qualified_name = "{}/{}{}".format(self.UPLOAD_PATH, file_id, ext)

        with open(qualified_name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_id, file_id + ext