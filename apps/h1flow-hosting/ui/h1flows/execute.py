from .mock_framework import H1StepWithWebUI


class Execute(H1StepWithWebUI):
    def get_response(self, req, isPost):
        return self.execute(None, None, None)

    def execute(self, model_id, inputs, user_id):
        return "This is Execute"