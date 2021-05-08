from .mock_framework import H1StepWithWebUI

class Home(H1StepWithWebUI):
    @staticmethod
    def get_response(req, isPost):
        return "<br/><br/><center><H1>Hello Human-First AI World!</H1></center>"