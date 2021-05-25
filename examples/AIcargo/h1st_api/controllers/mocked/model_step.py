from .step import H1Step


class H1ModelStep(H1Step):
    def __init__(self, model_id, model_platform, model_path=None, model_version=1):
        self.model_id = model_id
        self.model_platform = model_platform
        self.model_path = model_path
        self.model_version = model_version
