import base64
import requests
import io
from PIL import Image
import numpy as np
import json


TENSORFLOW_SERVER = "http://localhost:8501/v1/models"


class ModelExecutor:
    @staticmethod
    def execute(model_name, input_data, input_type='text'):
        raise NotImplementedError


class TensorFlowModelExecutor(ModelExecutor):
    @staticmethod
    def pre_process(input_data, spec):
        if 'input-caling' in spec:
            if 'mean' in spec['input-caling'] and 'std' in spect['input-caling']:
                mean, std = np.array(spec['input-caling']['mean']), np.array(spec['input-caling']['std'])
                return (input_data - mean) / std
            elif 'min' in spec['input-caling'] and 'max' in spect['input-caling']:
                min, max = np.array(spec['input-caling']['min']), np.array(spec['input-caling']['max'])
                return (input_data - min) / (max - min)
        return input_data
    def post_process(output, spec):
        if 'output-mapping' in spec:
            return spec['output-mapping'][output]
        return output
    
    @staticmethod
    def execute(model_name, input_data, input_type='text', spec={}):
        server_url = '{host}/{model_name}:predict'.format(host=TENSORFLOW_SERVER, model_name=model_name)

        # image input
        if input_type == 'image':
            input_format = spec['input-format']
            im = Image.open(io.BytesIO(input_data))

            # convert to corresponding mode if needed
            if 'image-mode' in spec:
                im = im.convert(spec['image-mode'])

            # resize image
            if 'image-shape' in spec:
                im = im.resize(spec['image-shape'])

            if input_format == 'image_bytes':
                img_byte_arr = io.BytesIO()
                im.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                # Compose a JSON Predict request (send JPEG image in base64).
                jpeg_bytes = base64.b64encode(img_byte_arr).decode('utf-8')
                # print('jpeg_bytes', jpeg_bytes)
                predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes
            elif input_format == 'numpy':
                input_arr = np.array(im)
                print(input_arr.shape)
                predict_request = {"instances": [{"images":input_arr.tolist()}]}
                predict_request = json.dumps(predict_request)

            # Send request
            response = requests.post(server_url, data=predict_request)
            response.raise_for_status()
            prediction = response.json()['predictions'][0]
            print(prediction['classes'])
            return TensorFlowModelExecutor.post_process(prediction['classes'], spec)
        
        elif input_type=='text':
            # text input
            predict_request = '{"inputs" : ["%s"]}' % input_data
            response = requests.post(server_url, data=predict_request)
            response.raise_for_status()
            prediction = response.json()['outputs']['prediction']
            return prediction


class PyTorchModelExecutor(ModelExecutor):
    @staticmethod
    def execute(model_name, input_data, input_type='text'):
        pass
