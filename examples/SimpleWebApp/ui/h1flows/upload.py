from .mock_framework import H1StepWithWebUI
from django.http import HttpResponse
from django.template import Context, loader
import os
class Upload(H1StepWithWebUI):
    def handle_get(self, req, is_post, *args, **kwargs):
        __template = """
            <html>
            <head>
                <title>Model Upload</title>
            </head>
            <body>
            Upload An Image
            <form method=POST enctype=multipart/form-data action="">
                <label for="text">Model name:</label><br>
                <input type="text" id="model_name" name="model_name"><br>
                <label for="input_type">Input type:</label><br>
                <select name="input_type" id="input_type">
                    <option value="image">Image</option>
                    <option value="text">text</option>
                </select><br>
                <label for="model_package">Model Package:</label><br>
                <input type="file" name="model_package">
                <input type="submit">
            </form>
            </body>
            </html>
            """
        return __template

    def handle_post(self, req, *args, **kwargs):
        model_package=req.FILES['model_package']
        # Write to file???
        model_name = req.POST['model_name']
        input_type = req.POST['input_type']
        share_url = H1ModelManager.upload_model({'model_name': model_name,
                                    'input_type': input_type,
                                    'model_package': model_package
                                    })

        return share_url

    
    