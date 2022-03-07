from typing import Any, Dict
from h1st.model.modelable import Modelable
from h1st.model.rule_based_model import RuleBasedModel
from .modeler import Modeler

class RuleBasedModeler(Modeler):
    def __init__(self, model_class=RuleBasedModel):
        self.model_class = model_class

    def build_model(self, data: Dict[str, Any] = None) -> RuleBasedModel:
        return self.model_class()