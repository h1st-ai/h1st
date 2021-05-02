import base64
import requests


TENSORFLOW_SERVER = "http://localhost:8501/v1/models"
PYTORCH_SERVER = "http://localhost:8080"


class ModelExecutor:
    @staticmethod
    def execute(model_name, input_data, func, input_type):
        raise NotImplementedError


class TensorFlowModelExecutor(ModelExecutor):
    @staticmethod
    def execute(model_name, input_data, func='predictions', input_type='text'):
        server_url = '{host}/{model_name}:predict'.format(host=TENSORFLOW_SERVER, model_name=model_name)

        # image input
        if input_type == 'image':
            
            # Compose a JSON Predict request (send JPEG image in base64).
            jpeg_bytes = base64.b64encode(input_data).decode('utf-8')
            print('jpeg_bytes', jpeg_bytes)
            predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

            # Send request
            response = requests.post(server_url, data=predict_request)
            response.raise_for_status()
            prediction = response.json()['predictions'][0]
            return prediction['classes']
        
        elif input_type == 'text':
            # text input
            predict_request = '{"inputs" : ["%s"]}' % input_data
            response = requests.post(server_url, data=predict_request)
            response.raise_for_status()
            prediction = response.json()['outputs']['prediction']
            return prediction

        raise NotImplementedError


class PyTorchModelExecutor(ModelExecutor):
    @staticmethod
    def execute(model_name, input_data, func='predictions', input_type='image'):
        server_url = '{host}/{func}/{model_name}'.format(host=PYTORCH_SERVER, func=func, model_name=model_name)
        if input_type == 'image':
            files = {
                'data': (input_data, open(input_data, 'rb')),
            }
            response = requests.post(server_url, files=files)
            return response.json()

        raise NotImplementedError
