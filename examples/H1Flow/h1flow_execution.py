from h1 import H1FlowManager, H1FlowExecutor, H1Flow, H1StepWithUI, H1WebUI

def execute_flow_0():
    H1FlowExecutor.execute(flow_id='image_classification')

def execute_flow_1():
    # This assumes that the H1FlowManager keeps track of flows
    flow = H1FlowManager.get_flow(flow_id='image_classification')
    H1FlowExecutor.execute(flow)

def execute_flow_2():
    # This assumes that the flow was defined in a python file
    from image_classification_flow import ImageClassificationFlow
    flow = ImageClassificationFlow()
    H1FlowExecutor.execute(flow=flow)

def execute_flow_3():
    # Here we define the flow with the step

    class ImageClassificationWebUI(H1WebUI):
        def __init__(self):
            self.template = """
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

    class ImageClassificationStep(H1StepWithUI):
        def __init__(self):
            self.model = H1FlowManager.get_model('image_classification_tf_2.0_by_nhan')
            self.ui = ImageClassificationWebUI()

        def call(self, input_data):
            image = input_data['image']
            prediction = self.model.predict(image)

            return {'class': prediction}

    class ImageClassificationFlow(H1Flow):
        def __init__(self):
            self.start()\
                .add(ImageClassificationStep())\
                .end()

    flow = ImageClassificationFlow()
    H1FlowExecutor.execute(flow=flow)

if __name__ == '__main__':
    execute_flow_0()
