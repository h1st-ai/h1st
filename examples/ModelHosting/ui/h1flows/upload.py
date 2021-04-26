from .mock_framework import H1StepWithWebUI
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

class Upload(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req):
        return self.handle_post(req)
    
    def handle_post(self, req):
        print('Raw Data:')
        print(req.body)
        return HttpResponse("Done") 

    def handle_uploaded_file(f):
        with open('some/file/name.txt', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)