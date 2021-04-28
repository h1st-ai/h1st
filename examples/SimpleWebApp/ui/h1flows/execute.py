from .mock_framework import H1StepWithWebUI
from .model_executor import TensorFlowModelExecutor
from django import forms

class Execute(H1StepWithWebUI):
    def get_response(self, req, is_post, *args, **kwargs):
        print(req.GET)
        print(req.POST)
        print(kwargs)
        print(args)
        model_id = kwargs['model_id']
        if model_id == 'image_classification':
            if is_post:
                return self.execute(model_id, input_data=req.FILES['image'].read(), input_type='image')
            
            return """
                    <h1> Image Classification </h1>
                    <form enctype="multipart/form-data" action="/execute/image_classification" method='POST'>
                    <input type="file" id="myFile" name="image"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """

        elif model_id == 'sentiment_analysis':
            if is_post:
                return self.execute(model_id, input_data=req.POST['text'], input_type='text')
            
            return """
                    <h1> Sentiment analysis </h1>
                    <form action="/execute/sentiment_analysis" method='POST'>
                    <label for="text">Text:</label><br>
                    <input type="text" id="text" name="text"><br>
                    <input type="submit" value='Classify'>
                    </form>
                    """

    def execute(self, model_id, input_data, input_type):
        return TensorFlowModelExecutor.execute(model_id, input_data, input_type=input_type)
