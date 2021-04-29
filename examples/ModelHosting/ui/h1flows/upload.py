from .mock_framework import H1StepWithWebUI
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os 


class Upload(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req):
        return self.handle_post(req)
    
    def handle_post(self, req):
        self.handle_uploaded_file(req.FILES['file'])
        return HttpResponse("Done") 

    def handle_uploaded_file(self, f):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        with open("models", 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)