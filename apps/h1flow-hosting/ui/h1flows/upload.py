from .mock_framework import H1StepWithWebUI


class Upload(H1StepWithWebUI):
    def get_response(self, req, isPost):
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

        return __template