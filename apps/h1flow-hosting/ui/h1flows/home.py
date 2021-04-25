from .mock_framework import H1StepWithWebUI


class Home(H1StepWithWebUI):
    def get_response(self, req, isPost):
        return "This is Home"