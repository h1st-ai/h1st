from .mock_framework import H1StepWithWebUI
from .model_executor import TensorFlowModelExecutor, PyTorchModelExecutor
from django import forms
import numpy as np
import json

class Execute(H1StepWithWebUI):
    def get_response(self, req, is_post, *args, **kwargs):
        model_id = kwargs['model_id']
        # TODO: model_type, input_type and spec should be loaded from DB instead
        tensorflow_text_models = ['sentiment_analysis', 'text_classification_keras_tfhub', 'movie_review_classifier']
        
        pytorch_image_models = ['alexnet', 'resnet-18', 'fcn_resnet_101', 'fastrcnn']
        pytorch_text_models = ['my_text_classifier']

        if model_id in pytorch_image_models + pytorch_text_models:
            model_type = 'pytorch'
        else:
            model_type = 'tensorflow'
        
        if 'imagenet' in model_id or model_id in pytorch_image_models:
            input_type = 'image'
        elif model_id in tensorflow_text_models + pytorch_text_models:
            input_type = 'text'
        
        if model_type =='tensorflow':
            spec = json.load(open('io-spec/%s.json' % model_id))
        else:
            spec = {}
        
        if input_type == 'image':
            if is_post:
                uploaded_file = req.FILES['image']
                if uploaded_file.size > 200 * 1024:
                    return "Sorry, we accept only images with size <= 200KB"
                image_data = uploaded_file.read()
                return json.dumps(self.execute(model_id, model_type, input_data=image_data, input_type='image', spec=spec))
            
            return """
                    <h1> Image Classification </h1>
                    <form enctype="multipart/form-data" action="/execute/%s" method='POST'>
                    <input type="file" id="myFile" name="image"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """ % (model_id)

        elif input_type == 'text':
            if is_post:
                return self.execute(model_id, model_type, input_data=req.POST['text'], input_type='text', spec=spec)
            
            return """
                    <h1> Sentiment analysis </h1>
                    <form action="/execute/%s" method='POST'>
                    <label for="text">Text:</label><br>
                    <input type="text" id="text" name="text"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """ % (model_id)

    def execute(self, model_id, model_type, input_data, input_type, spec):
        if model_type == 'pytorch':
            # PyTorch models
            return PyTorchModelExecutor.execute(model_id, input_data, input_type=input_type, spec=spec)
        elif model_type == 'tensorflow':
            return TensorFlowModelExecutor.execute(model_id, input_data, input_type=input_type, spec=spec)

        raise NotImplementedError('Currently, only Tensorflow 2.x and PyTorch models are supported')