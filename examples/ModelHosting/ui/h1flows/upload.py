from .mock_framework import H1StepWithWebUI
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import os 
import uuid
import json

from ui.frameworks.django.app.models import AIModel
class Upload(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req):
        return self.handle_post(req)
    
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

            print(name, description, input, output, file_name)

            m = AIModel(
                name=name,
                description=description,
                model_input=model_input,
                model_output=model_output,
                file_name=file_name
            )

            m.save()

            return JsonResponse({
                "status": "OK",
                "id": m.id
            }) 

        # # if there is a file, upload. Otherwise, check for form input
        # if file is None:
        #     return HttpResponseBadRequest({
        #         "status": "Bad request"
        #     })
        # else:
            

    def handle_uploaded_file(self, f):
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(str(f))[1]

        print("Saving " + ext)
        
        # start with <id>.uploaded.<ext>. After unzipping, remove uploaded
        with open("uploaded/" + file_id + ".uploaded" + ext, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_id + ext