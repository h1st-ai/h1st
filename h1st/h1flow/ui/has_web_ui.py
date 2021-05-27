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
        raise NotImplementedError('Please implement get method handler')
    
    def handle_post(self, req):
        raise NotImplementedError('Please implement post method handler')

    def handle_put(self, req):
        raise NotImplementedError('Please implement put method handler')

    def handle_delete(self, req):
        raise NotImplementedError('Please implement delete method handler')
    
    def handle_default(self, req):
        raise NotImplementedError('Method is not supported')