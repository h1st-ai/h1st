from .mock_framework import H1StepWithWebUI
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import os 
import uuid
import json

# from ui.frameworks.django.app.models import AIModel
from .models import AIModel
class Upload(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req):
        if (req.method == 'GET'):
            return self.handle_get(req)
        elif (req.method == 'POST'):
            return self.handle_post(req)
        elif (req.method == 'PUT'):
            return self.handle_post(req)
        elif (req.method == 'DELETE'):
            return self.handle_post(req)
        else:
            return self.handle_default(req)

    def handle_get(self, req):
        user = "mocked_user"
        models = list(AIModel.objects.filter().values())

        # add paging
        return JsonResponse({
            'status': 'OK',
            'result': models
        })
    
    def handle_post(self, req):
        try:
            file = req.FILES['file']
            file_id = self.handle_uploaded_file(file)

            return JsonResponse({
                "status": "OK",
                "id": file_id
            }) 
        except:
            data = json.loads(req.body)
            name = data['name']
            description = data['description']
            model_input = data['input']
            model_output = data['output']
            file_name = data['uploadedFile']
            creator="mocked_user"

            m = AIModel(
                name=name,
                description=description,
                model_input=model_input,
                model_output=model_output,
                file_name=file_name,
                creator=creator
            )

            m.save()

            return JsonResponse({
                "status": "OK",
                "result": {
                    'id': m.id,
                    'name': name,
                    'description': description,
                    'model_input': model_input,
                    'model_output': model_output,
                    'created_at': m.created_at,
                    'updated_at': m.updated_at,
                    'creator': 'mocked_user'
                }
            }) 
            
    def handle_uploaded_file(self, f):
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(str(f))[1]

        print("Saving " + ext)
        
        # start with <id>.uploaded.<ext>. After unzipping, remove uploaded
        with open("uploaded/" + file_id + ".uploaded" + ext, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_id + ext