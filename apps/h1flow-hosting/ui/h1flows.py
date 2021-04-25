# from h1 import H1FlowManager, H1FlowExecutor, H1Flow, H1StepWithUI, H1WebUI
from abc import abstractclassmethod, ABC
from django.http import HttpResponse


'''
UC2: Execute Model

* User_X arrives at a page publicized by its DS owner, or listed in some directory
* The URL will already identify the model (actually, H1Flow or H1Step) to be executed
* The user may be authenticated, or not (anonymous)
* The H1Flow/H1Step execution/evaluation will take place in the backend either as (a) the authenticated user, or (b) the anonymous user
* The inputs to the H1Flow/H1Step will come from the web page input fields
* The outputs from the H1Flow/H1Step will be returned as a web output

'''

class HasWebUI(ABC):
    def handle_request(self, req):

        if (req.method == 'GET'):
            return self.handle_get(req)
        
        return self.handle_post(req)
    
    def handle_post(self, req):
        pass

    def handle_get(self, req):
        pass

class H1Step():
    def __init__(self):
        pass

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass

class Home(H1StepWithWebUI):
    def handle_get(self, req):
        __template = """
            <html>
            <head>
                <title>Image Classification</title>
            </head>
            <body>
            List of models
            </body>
            </html>
            """

        return HttpResponse(__template)

class Upload(H1StepWithWebUI):
    def handle_get(self, req):
        __template = """
            <html>
            <head>
                <title>Image Classification</title>
            </head>
            <body>
            Upload An Image
            <form method=POST enctype=multipart/form-data action="{{ url_for('upload') }}">
                <input type=file name=image>
                <input type="submit">
            </form>
            Classification Result: {{data.class}}
            </body>
            </html>
            """

        return HttpResponse(__template)


# class Execute_Model(H1Step, HasWebUi):
class Execute(H1StepWithWebUI):

    # def __init__():
    #     self.template = """
    #                     <html>
    #                     <head>
    #                         <title>Image Classification</title>
    #                     </head>
    #                     <body>
    #                     Upload An Image
    #                     <form method=POST enctype=multipart/form-data action="{{ url_for('upload') }}">
    #                         <input type=file name=image>
    #                         <input type="submit">
    #                     </form>
    #                     Classification Result: {{data.class}}
    #                     </body>
    #                     </html>
    #                     """

    #
    # HasWebUi implementation
    #
    def handle_get(self, req):
        # model_params = ModelManager.get_model_params(request.query_string['id'])
        # return ... # call django render with template and parameters

        __template = """
            <html>
            <head>
                <title>Image Classification</title>
            </head>
            <body>
            Result: 1
            </body>
            </html>
            """

        return HttpResponse(__template)

    # @post('/execute_model')
    # def handle_post(self, request, body):
    #     model_params = ModelManager.get_model_params(body.model_id)
    #     result = self.execute(body.model_id, body.model_inputs, request.user_id)
    #     render_response(result, model_params.output_type)

    #
    # H1Step implementation
    #
    def execute(self, model_id, inputs, user_id):
        pass


URL_MAP = {
    "": Home,
    "upload/": Upload,
    "execute/": Execute,
}
