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

from .model_saver import ModelSaver
from .model_manager import TensorFlowModelManager
from h1st_api.models import ModelClass

from h1st_api.models import AIModel
from django.conf import settings

logger = logging.getLogger(__name__)
class Upload(APIView):
    def __init__(self):
        super().__init__()
        self.FILE_SYSTEM = settings.FILE_SYSTEM  # local, s3
        self.FILE_SYSTEM_PREFIX = settings.FILE_SYSTEM_PREFIX
        self.UPLOAD_PATH = settings.UPLOAD_PATH
        # self.MODEL_PATH_PREFIX = settings.MODEL_PATH_PREFIX
        self.TF_PATH = settings.TF_PATH
        # self.TF_MODEL_CONFIG = "{}/models.config".format(self.TF_PATH)
        self.TF_MODEL_IO_FILE = settings.TF_MODEL_IO_FILE
    
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
        file = request.FILES.get('file', None)

        if file is not None:
            try:
                file_name, file_id = self.handle_uploaded_file(file)
            except Exception as ex:
                capture_exception(ex);

                return Response({
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "status": "OK",
                "id": file_id
            })
        else:
            try:
                data = request.data
                name = data['name']
                description = data['description']
                model_input = data['input']
                model_output = data['output']
                file_name = data['uploadedFile']
                type = data['type']
                creator=request.user
            except KeyError as ex:
                logger.error(ex)
                capture_exception(ex)

                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                }, status=status.HTTP_400_BAD_REQUEST)

            if type == ModelClass.TF:
                #deploy the model first
                file_path = "{}/{}".format(self.UPLOAD_PATH, file_name)
                dir_name = file_name.split('.')[0]
                deploy_result, config_data = self.deploy_tf_model(dir_name, file_path, model_type=type)

                print("deploy_result", deploy_result)
                
                if deploy_result['success'] is False:
                    return Response({
                        "status": "DEPLOYMENT_ERROR",
                        "message": "Error deploying model"
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

            # print("TYPE", type(m.creator))

            return Response({
                "status": "OK",
                "result": {
                    'id': m.id,
                    'model_id':dir_name,
                    'name': name,
                    'description': description,
                    'created_at': m.created_at,
                    'updated_at': m.updated_at,
                    'creator': str(m.creator)
                }
            })      

    # def create_model_config(self):
    #     os.mkdir(self.MODEL_PATH_PREFIX)
    #     os.mkdir(self.TF_PATH)
    #     with open(self.TF_MODEL_CONFIG, 'a') as out:
    #         out.write(f'model_config_list {{}}' + '\n')
    
    def deploy_tf_model(self, dir_name, file_path, model_type = ModelClass.TF):
        logger.info('Deploying TF model {}'.format(dir_name))
        if model_type == ModelClass.TF :
            # check to see if the directory exist
            # if not os.path.exists(self.MODEL_PATH_PREFIX):
            #     self.create_model_config()

            destination = '{}/{}'.format(self.TF_PATH, dir_name)
            logger.debug('Destination folder: {}'.format(destination))
            
            try:
                with ZipFile(file_path, 'r') as Z:
                    # Search for model-io.json
                    folder = None
                    # logger.debug(Z.namelist())
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
                logger.debug(folders)
                # search for folder with saved_model.pb file
                model_folder = None
                for _, folder in enumerate(folders):
                    folder_items = os.listdir(os.path.join(destination, folder))
                    logger.debug(folder_items)
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
                logger.info('Try loading model and get prediction.')
                loaded_model = tf.saved_model.load(new_folder_name)
                if 'serving_default' in loaded_model.signatures:
                    logger.debug('serving_default signature found.')
                    infer = loaded_model.signatures['serving_default']
                    logger.debug(infer.structured_input_signature)
                    input_key = list(infer.structured_input_signature[1])[0]
                    logger.debug(infer.structured_input_signature)
                    shape = infer.structured_input_signature[1][input_key].shape.as_list()
                    shape = [d if d is not None else 1 for d in shape]
                    # logger.debug(infer(tf.ones(shape)).keys())
                    # logger.debug('Successfully load and generate prediction')

                # Save the directory to the corresponding location
                # for example s3 if the target file system is not local
                saver = ModelSaver.get_saver(self.FILE_SYSTEM)
                ret = saver.save(destination, self.FILE_SYSTEM_PREFIX + destination)
                if not ret['success']:
                    raise RuntimeError(ret['message'])
                
                # Register the model
                base_path = self.FILE_SYSTEM_PREFIX + destination
                if saver.exists(base_path):
                    logger.info('Registering the model with TFServing')
                    TensorFlowModelManager.register_new_model_grpc(name=dir_name, base_path=base_path)
                else:
                    ex = 'No model directory exist at %s' % base_path
                    capture_exception(ex)
                    raise RuntimeError(ex)
                
                # read model.io.json
                config_data = self.handle_modelio_json(path='{}/{}/{}'.format(self.TF_PATH, dir_name, self.TF_MODEL_IO_FILE))

                # if self.FILE_SYSTEM != 'local':
                #     shutil.rmtree(destination)

                # remove zip file
                # os.remove(file_path)
                return {'success': True, }, config_data

            except Exception as ex:
                capture_exception(ex)
                logger.info(type(ex))    # the exception
                logger.info(ex.args)     # arguments stored in .args
                logger.info(ex)          # __str__ allows args to be printed directly,
                
                # Remove the extracted folder
                # if os.path.exists(destination):
                #     shutil.rmtree(destination)
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