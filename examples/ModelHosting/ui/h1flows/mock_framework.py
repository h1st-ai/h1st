from django.http import HttpResponse

class HasWebUI():
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
        raise NotImplementedError('Method not supported')
    
    def handle_post(self, req):
        raise NotImplementedError('Method not supported')
        
    def handle_put(self, req):
        raise NotImplementedError('Method not supported')

    def handle_delete(self, req):
        raise NotImplementedError('Method not supported')
    
    def handle_default(self, req):
        raise NotImplementedError('Method not supported')


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
