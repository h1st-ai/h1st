from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from sentry_sdk import capture_exception

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import zipfile36 as zipfile
import os 
import shutil
import os.path
import uuid
import json
from zipfile import ZipFile
import tensorflow as tf
import logging

from .model_manager import TensorFlowModelManager
from h1st_api.models import ModelClass

from h1st_api.models import AIModel
class Upload(APIView):
    def __init__(self):
        super().__init__()
        self.UPLOAD_PATH = "uploaded"
        self.MODEL_EXT_PATH = "model_repo"
        self.TF_PATH = "{}/tensorflow_models".format(self.MODEL_EXT_PATH)
        self.TF_MODEL_CONFIG = "{}/models.config".format(self.TF_PATH)
        self.TF_MODEL_IO_FILE = "model-io.json"
    
    def get(self, request, format=None):
        """
        Return a list of applications for the current user
        """
        models = list(AIModel.objects.filter(creator=request.user).only('id', 'name', 'description', 'type', 'creator', 'status').values())

        return JsonResponse({
            'status': 'OK',
            'result': models
        })
    
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
            creator=request.user

            if type == ModelClass.TF:
                #deploy the model first
                file_path = "{}/{}".format(self.UPLOAD_PATH, file_name)
                dir_name = file_name.split('.')[0]
                deploy_result, config_data = self.deploy_tf_model(dir_name, file_path, model_type=type)

                print("DEPLOYYY", deploy_result)
                
                if deploy_result['success'] is False:
                    return Response({
                        "status": "DEPLOYMENT_ERROR",
                        "message": deploy_result['message']
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

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

            # print("M_USER", m.creator, type(m.creator))

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
                    'creator': "mocked_user"
                }
            })

    def create_model_config(self):
        os.mkdir(self.MODEL_EXT_PATH)
        os.mkdir(self.TF_PATH)
        with open(self.TF_MODEL_CONFIG, 'a') as out:
            out.write(f'model_config_list {{}}' + '\n')
    
    def deploy_tf_model(self, dir_name, file_path, model_type = ModelClass.TF):
        if model_type == ModelClass.TF :
            # check to see if the directory exist
            if not os.path.exists(self.MODEL_EXT_PATH):
                self.create_model_config()

            destination = '{}/{}'.format(self.TF_PATH, dir_name)
            try:
                with ZipFile(file_path, 'r') as Z:
                    # Search for model-io.json
                    folder = None
                    # logging.debug(Z.namelist())
                    for elem in Z.namelist():
                        if '/' + self.TF_MODEL_IO_FILE in elem or elem == self.TF_MODEL_IO_FILE:
                            folder = elem.split('/')[:-1]
                            break
                    if folder is None:
                        raise RuntimeError('{} not found!!!'.format(self.TF_MODEL_IO_FILE))

                    Z.extractall(path=destination)
                    if len(folder) > 0:
                        # nested folder, move the model directory and 
                        source_folder = destination + '/' + '/'.join(folder)
                        target_folder = destination
                        file_names = os.listdir(source_folder)
                        for file_name in file_names:
                            shutil.move(os.path.join(source_folder, file_name), target_folder)
                        shutil.rmtree(source_folder)

                # Search for a folder with SavedModel artifacts
                items = os.listdir(destination)
                folders = [item for item in items if os.path.isdir(os.path.join(destination, item))]
                logging.debug(folders)
                # search for folder with saved_model.pb file
                model_folder = None
                for _, folder in enumerate(folders):
                    folder_items = os.listdir(os.path.join(destination, folder))
                    logging.debug(folder_items)
                    if 'saved_model.pb' in folder_items or 'saved_model.pbtxt' in folder_items:
                        model_folder = folder
                        break

                if model_folder is None:
                    raise RuntimeError('No folder with SavedModel artifacts found')
                
                # Rename this model folder into `1`
                new_folder_name = '{}/1'.format(destination)
                os.rename('{}/{}'.format(destination, model_folder), new_folder_name)

                # Check if we can get prediction from the model
                # For now, we assume the default `serving_default` signature and only 1 input
                # Any error will be thrown
                # TODO: capture and throw the right error
                logging.debug('Try loading model and get prediction.')
                loaded_model = tf.saved_model.load(new_folder_name)
                if 'serving_default' in loaded_model.signatures:
                    logging.debug('serving_default signature found.')
                    infer = loaded_model.signatures['serving_default']
                    logging.debug(infer.structured_input_signature)
                    input_key = list(infer.structured_input_signature[1])[0]
                    logging.debug(infer.structured_input_signature)
                    shape = infer.structured_input_signature[1][input_key].shape.as_list()
                    shape = [d if d is not None else 1 for d in shape]
                    # logging.debug(infer(tf.ones(shape)).keys())
                    # logging.debug('Successfully load and generate prediction')

                # consider deleting the uploaded file at this point
                # TensorFlowModelManager.register_new_model(conf_filepath=self.TF_MODEL_CONFIG, name=dir_name, base_path="/models/{}/".format(dir_name))
                if os.path.exists(destination):
                    logging.debug('Registering the model with TFServing')
                    TensorFlowModelManager.register_new_model_grpc(name=dir_name, base_path="/models/{}/".format(dir_name))
                else:
                    ex = 'No model directory exist at %s' % destination
                    # capture_exception(ex)
                    raise RuntimeError(ex)
                
                # read model.io.json
                config_data = self.handle_modelio_json(path='{}/{}/{}'.format(self.TF_PATH, dir_name, self.TF_MODEL_IO_FILE))

                # remove zip file
                os.remove(file_path)
                return {'success': True, }, config_data

            except Exception as ex:
                # capture_exception(ex)
                logging.info(type(ex))    # the exception
                logging.info(ex.args)     # arguments stored in .args
                logging.info(ex)          # __str__ allows args to be printed directly,
                
                # Remove the extracted folder
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                return {'success': False, 'message': ex.__str__}, None
        
        return {'success': False, 'message': 'Unsupported model type'}, None
    
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