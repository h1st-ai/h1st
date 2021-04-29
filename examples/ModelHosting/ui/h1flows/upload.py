from .mock_framework import H1StepWithWebUI
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
import os 
import uuid


class Upload(H1StepWithWebUI):
    @csrf_exempt
    def handle_request(self, req):
        return self.handle_post(req)
    
    def handle_post(self, req):
        file = req.FILES['file']
        
        if file is None:
            return HttpResponseBadRequest({
                "status": "Bad request"
            })

        file_id = self.handle_uploaded_file(file)

        return JsonResponse({
            "status": "OK",
            "id": file_id
        }) 

        # try:
        #     print(file)
        #     self.handle_uploaded_file(file)

        #     return JsonResponse({
        #         "status": "OK",
        #         "id": ""
        #     }) 
        # except:
        #     return HttpResponseServerError({
        #         "status": "Server error",
        #         "message": ex
        #     })

    def handle_uploaded_file(self, f):
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(str(f))[1]

        print("Saving " + ext)
        
        with open("uploaded/" + file_id + ext, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        return file_id + ext