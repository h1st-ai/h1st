from h1st.model.modeler import Modeler
from h1st.model.ensemble.ensemble import LogicalOREnsemble


class EnsembleModeler(Modeler):
    pass


class LogicalOREnsembleModeler(Modeler):
    def __init__(self):
        super().__init__()
        self.model_class = LogicalOREnsemble

    def build_model(self) -> LogicalOREnsemble:
        return self.model_class
