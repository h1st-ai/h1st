from django.http import HttpResponse

class HasWebUI():
    def handle_request(self, req):
        if (req.method == 'GET'):
            return self.handle_get(req)
        else:
            return self.handle_post(req)
    
    def handle_post(self, req):
        return HttpResponse(self.get_response(req, True))

    def handle_get(self, req):
        return HttpResponse(self.get_response(req, False))

    def get_response(self, req, isPost=False):
        return 'Please override get_response()'


class H1Step():
    def __init__(self):
        pass

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass


class HasCreatReactApp(H1Step, HasWebUI): 
    def __init__(self, path):
        self.path = path
    
    def handle_request(self):
        pass
