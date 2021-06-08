from .mocked.model_step import H1ModelStep

from PIL import Image, ImageOps

import base64
import os
import io
import json
import numpy as np
import requests

from .model_manager import TensorFlowModelManager
from .model_saver import ModelSaver

import logging
logger = logging.getLogger(__name__)

TENSORFLOW_SERVER = os.getenv("TENSORFLOW_SERVER", "http://localhost:8501/v1/models")
PYTORCH_SERVER = os.getenv("PYTORCH_SERVER", "http://localhost:8080")

# Need to set the right number,
# given that the complex models may need a bit time to run 
TIMEOUT = 100 # seconds

class ModelExecutor:
    @staticmethod
    def execute(model_step: H1ModelStep, input_data, input_type, config={}, spec={}):
        if model_step.model_platform == 'tensorflow':
            return TensorFlowModelExecutor.execute(model_step.model_id, input_data, input_type=input_type, spec=spec)
        if model_step.model_platform == 'pytorch':
            return PyTorchModelExecutor.execute(model_step.model_id, input_data, input_type=input_type, spec=spec)
        return NotImplementedError


class TensorFlowModelExecutor:
    @staticmethod
    def pre_process(input_data, spec):
        print("preprocess", input_data.shape)
        if 'input-scaling' in spec:
            if 'input-mean' in spec['input-scaling'] and 'input-std' in spec['input-scaling']:
                logger.debug('Perform normalization')
                mean, std = np.array(spec['input-scaling']['input-mean']), np.array(spec['input-scaling']['input-std'])
                return (input_data - mean) / std
            elif 'input-min' in spec['input-scaling'] and 'input-max' in spec['input-scaling']:
                logger.debug('Perform min-max scaling')
                input_min = np.array(spec['input-scaling']['input-min'])
                input_max = np.array(spec['input-scaling']['input-max'])
                target_min = np.array(spec['input-scaling']['target-min'])
                target_max = np.array(spec['input-scaling']['target-max'])
                return ((input_data - input_min) / (input_max - input_min)
                        * (target_max - target_min) + target_min)
        return input_data
    
    @staticmethod
    def post_process(output, spec):
        ret = output.copy()
        if len(ret) == 1:
            # Binary classification??? how to handle this?
            pass
        else:
            if 'output-mapping' in spec:
                logger.debug('Perform output mapping')
                # print(dict(zip(spec['output-mapping'], ret)))
                ret = sorted(zip(spec['output-mapping'], ret), key=lambda x: -x[1])
            if 'output-limit' in spec:
                ret = dict(ret[:spec['output-limit']])
        return ret
    
    @staticmethod
    def send_prediction_request(server_url, model_name, predict_request, config):
        response = requests.post(server_url, data=predict_request, timeout=TIMEOUT)
        logger.info('Response time: %d seconds' % response.elapsed.total_seconds())
        if response.status_code == 404:
            logger.info('Model not found in TFServing. Re-register the model and request again')
            
            saver = ModelSaver.get_saver(config.FILE_SYSTEM)
            base_path = config.FILE_SYSTEM_PREFIX + '{}/{}'.format(config.TF_PATH, model_name)
            if saver.exists(base_path):
                if TensorFlowModelManager.register_new_model_grpc(name=model_name, base_path=base_path):
                    response = requests.post(server_url, data=predict_request, timeout=TIMEOUT)
                    response.raise_for_status()
                    logger.info('Response time: %d seconds' % response.elapsed.total_seconds())
            else:
                logger.info('Model not found in TFServing')
                raise RuntimeError('Model not found')
        else:
            response.raise_for_status()

        return response.json()

    @staticmethod
    def execute(model_name, input_data, input_type='text', config={}, spec={}):
        logger.info('Execute model {}'.format(model_name))
        server_url = '{host}/{model_name}:predict'.format(host=TENSORFLOW_SERVER, model_name=model_name)

        # image input
        if input_type == 'image':
            try:
                input_format = spec['input-format']
            except KeyError:
                input_format = "numpy"

            im = Image.open(io.BytesIO(input_data))

            # convert to corresponding color mode if needed
            if 'input-image-mode' in spec:
                color_mode = spec['input-image-mode'].upper()
            else:
                color_mode = 'RGB'
            if im.mode != color_mode:
                im = im.convert(color_mode)

            # resize image
            if 'input-image-shape' in spec:
                # This is from Gradio's Image Input widget's code
                center = (0.5, 0.5)
                im = ImageOps.fit(im, spec['input-image-shape'], centering=center)

            if input_format == 'image_bytes':
                logger.debug('Raw Image Bytes Input')
                img_byte_arr = io.BytesIO()
                im.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                # Compose a JSON Predict request (send JPEG image in base64).
                jpeg_bytes = base64.b64encode(img_byte_arr).decode('utf-8')
                predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes
            elif input_format == 'numpy':
                logger.debug('Numpy Input')
                input_arr = np.array(im)
                logger.debug(input_arr.shape)
                input_arr = TensorFlowModelExecutor.pre_process(input_arr, spec)
                # TODO: We must read the signature spec and craft the input correspondingly
                if model_name == 'imagenet_keras_mobilenetv2':
                    predict_request = {"instances": [{"input_image": input_arr.tolist()}]}
                else:
                    predict_request = {"instances": [input_arr.tolist()]}
                predict_request = json.dumps(predict_request)

            # Send request
            # TODO: Retry up to N times?
            # TODO: Check for error and return proper message
            
            response = TensorFlowModelExecutor.send_prediction_request(server_url, model_name, predict_request, config)
            
            prediction = response['predictions'][0]
            logger.debug(len(prediction))
            if 'classes' in prediction:
                # This is for Resnet with `image_bytes` input
                prediction = prediction['probabilities']
            
            return TensorFlowModelExecutor.post_process(prediction, spec)
        
        elif input_type=='text':
            # text input
            predict_request = '{"inputs" : ["%s"]}' % input_data
            
            response = TensorFlowModelExecutor.send_prediction_request(server_url, model_name, predict_request, config)
            
            prediction = response['outputs']
            # TODO: We must read the signature spec and extract outputs correspondingly
            if model_name == 'sentiment_analysis':
                prediction = prediction['prediction']
            return prediction


class PyTorchModelExecutor:
    @staticmethod
    def execute(model_name, input_data, func='predictions', input_type='image', spec={}):
        server_url = '{host}/{func}/{model_name}'.format(host=PYTORCH_SERVER, func=func, model_name=model_name)
        
        if input_type == 'image':
            data = {
                'data': input_data
            }

            # TODO: Retry up to N times?
            # TODO: Check for error and return proper message
            response = requests.post(server_url, data=data, timeout=TIMEOUT)
            logger.info('Response time: %d seconds' % response.elapsed.total_seconds())
            response.raise_for_status()
            return response.json()

        raise NotImplementedError
