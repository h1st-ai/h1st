from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

class HasWebUI():
    @csrf_exempt
    def handle_request(self, req, *args, **kwargs):
        if (req.method == 'GET'):
            return self.handle_get(req, *args, **kwargs)
        else:
            return self.handle_post(req, *args, **kwargs)
    
    def handle_post(self, req, *args, **kwargs):
        return HttpResponse(self.get_response(req, *args, **kwargs, is_post=True))

    def handle_get(self, req, *args, **kwargs):
        return HttpResponse(self.get_response(req, *args, **kwargs, is_post=False))

    def get_response(self, req, isPost=False, *args, **kwargs):
        return 'Please override get_response()'

class H1Step():
    def __init__(self):
        pass

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass