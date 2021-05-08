from .mock_framework import H1StepWithWebUI


class Home(H1StepWithWebUI):
    def get_response(self, req, isPost):
        return "<br/><br/><center><H1>Hello Human-First AI World, Tri!!!!</H1></center>"