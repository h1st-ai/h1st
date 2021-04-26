class HasWebUI():
    def handle_request(self, req):
        if (req.method == 'GET'):
            return self.handle_get(req)
        else:
            return self.handle_post(req)
    
    def handle_post(self, req):
        raise NotImplementedError('Please implement post method handler')

    def handle_get(self, req):
        raise NotImplementedError('Please implement get method handler')