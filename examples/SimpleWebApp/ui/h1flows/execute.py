from h1st.core.step import H1StepWithWebUI
from .model_executor import TensorFlowModelExecutor


class ModelExecutionStep(H1StepWithWebUI):
    def get_response(self, req, is_post):
        if is_post:
            return self.execute(req.model_id, req.input_data)
        return "Web UI"

    def execute(self, model_id, input_data):
        return TensorFlowModelExecutor.execute(model_id, input_data)
