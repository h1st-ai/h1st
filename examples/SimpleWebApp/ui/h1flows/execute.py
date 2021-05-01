from .mock_framework import H1StepWithWebUI
from .model_executor import TensorFlowModelExecutor
from django import forms
import numpy as np
import json

class Execute(H1StepWithWebUI):
    def get_response(self, req, is_post, *args, **kwargs):
        # print(req.GET)
        # print(req.POST)
        # print(kwargs)
        # print(args)
        model_id = kwargs['model_id']
        spec = json.load(open('/tmp/%s.json' % model_id))
        if model_id in ['imagenet_resnet', 'imagenet_keras_mobilenetv2']:
            if is_post:
                uploaded_file = req.FILES['image']
                if uploaded_file.size > 200 * 1024:
                    return "Sorry, we accept only images with size <= 200KB"
                image_data = uploaded_file.read()
                return self.execute(model_id, input_data=image_data, input_type='image', spec=spec)
            
            return """
                    <h1> Image Classification </h1>
                    <form enctype="multipart/form-data" action="/execute/%s" method='POST'>
                    <input type="file" id="myFile" name="image"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """ % (model_id)

        elif model_id == 'sentiment_analysis':
            if is_post:
                return self.execute(model_id, input_data=req.POST['text'], input_type='text', spec=spec)
            
            return """
                    <h1> Sentiment analysis </h1>
                    <form action="/execute/sentiment_analysis" method='POST'>
                    <label for="text">Text:</label><br>
                    <input type="text" id="text" name="text"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """

    def execute(self, model_id, input_data, input_type, spec):
        return TensorFlowModelExecutor.execute(model_id, input_data, input_type=input_type, spec=spec)
