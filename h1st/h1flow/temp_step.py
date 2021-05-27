from ..h1flow.ui.web_ui import HasWebUI

class H1Step():
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError('Please implement this method')

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass