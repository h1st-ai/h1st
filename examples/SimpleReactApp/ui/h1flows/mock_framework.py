from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

class HasUI():
    def __init__(self):
        pass

class HasWebUI(HasUI):
    def __init__(self):
        pass

    @classmethod
    def handle_request(cls, req):
        if (req.method == 'GET'):
            return cls.handle_get(req)
        else:
            return cls.handle_post(req)
    
    @classmethod
    def handle_post(cls, req):
        return HttpResponse(cls.get_response(req, True))

    @classmethod
    def handle_get(cls, req):
        return HttpResponse(cls.get_response(req, False))

    @classmethod
    def get_response(cls, req, isPost=False):
        return 'Please override get_response()'


class HasRestUI(HasUI):
    @classmethod
    @api_view(['GET','POST'])
    def handle_request(req):
        return Response("DEFAULT REST RESPONSE")


class H1Step():
    def __init__(self):
        pass

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass

class H1StepWithRestUI(H1Step, HasRestUI):
    def __init__(self):
        pass