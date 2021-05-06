from .mock_framework import H1StepWithWebUI
from .model_executor import TensorFlowModelExecutor
# from django import formsm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .models import AIModel

class Execute(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req, *args, **kwargs):
        if (req.method == 'GET'):
            return self.handle_get(req)
        elif (req.method == 'POST'):
            return self.handle_post(req, *args, **kwargs)
        elif (req.method == 'PUT'):
            return self.handle_post(req)
        elif (req.method == 'DELETE'):
            return self.handle_post(req)
        else:
            return self.handle_default(req)

    def handle_post(self, req, *args, **kwargs):
        model_id = kwargs['model_id']
        model = AIModel.objects.get(id=model_id)

        print("This is model")
        print(model)

        # result = self.execute(model_id, input_data=req.FILES['image'].read(), input_type='image')

        return JsonResponse({
            'status': 'OK',
            'code': model_to_dict(model)
        })

        # if model_id == 'image_classification':
        #     if is_post:
        #         return self.execute(model_id, input_data=req.FILES['image'].read(), input_type='image')
            
        #     return """
        #             <h1> Image Classification </h1>
        #             <form enctype="multipart/form-data" action="/execute/image_classification" method='POST'>
        #             <input type="file" id="myFile" name="image"><br>
        #             <input type="submit" value='Classify'>
        #             </form>
        #             """

        # elif model_id == 'sentiment_analysis':
        #     if is_post:
        #         return self.execute(model_id, input_data=req.POST['text'], input_type='text')
            
        #     return """
        #             <h1> Sentiment analysis </h1>
        #             <form action="/execute/sentiment_analysis" method='POST'>
        #             <label for="text">Text:</label><br>
        #             <input type="text" id="text" name="text"><br>
        #             <input type="submit" value='Classify'>
        #             </form>
        #             """

    def execute(self, model_id, input_data, input_type):
        return TensorFlowModelExecutor.execute(model_id, input_data, input_type=input_type)
