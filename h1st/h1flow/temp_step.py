from h1st.h1flow.ui.has_web_ui import HasWebUI

# __TODO__ remove this file

class H1Step():
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError('Please implement this method')

class H1StepWithWebUI(H1Step, HasWebUI):
    def __init__(self):
        pass