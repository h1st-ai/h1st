from h1st.core.step import H1StepWithWebUI
from django.http import HttpResponse
from django.template import Context, loader
import os
class Upload(H1StepWithWebUI):
    def handle_get(self, req):
        PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
        print('PROJECT_PATH', PROJECT_PATH)
        # os.path.join(PROJECT_PATH, 'media/')

        template = loader.get_template('ui/templates/upload.html')
        # template = loader.get_template('templates/upload.html')
        return HttpResponse(template.render({ "name": "Khoa"}))

        # __template = """
        #     <html>
        #     <head>
        #         <title>Image Classification</title>
        #     </head>
        #     <body>
        #     Upload An Image
        #     <form method=POST enctype=multipart/form-data action="{{ url_for('upload') }}">
        #         <input type=file name=image>
        #         <input type="submit">
        #     </form>
        #     Classification Result: {{data.class}}
        #     </body>
        #     </html>
        #     """

        # return __template
    