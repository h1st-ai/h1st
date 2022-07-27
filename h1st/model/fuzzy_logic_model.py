import logging
from typing import Dict, NoReturn

import skfuzzy
from skfuzzy import control as ctrl
from skfuzzy.control.term import Term

from h1st.model.ml_model import MLModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyLogicModel(MLModel):
    """
    This FuzzyLogicModel is one kind of rule-based model. You can encode your
    rules in a fuzzy way using variables with membership functions.
    Add variables and use those variables when defining rules.

    """
    def __init__(self):
        super().__init__()

    @classmethod
    def construct_model(
        cls, 
        fuzzy_rules: list[skfuzzy.control.rule.Rule], 
        consequents: list
    ):
        model = cls()
        ctrl_system = ctrl.ControlSystem(fuzzy_rules)
        model.base_model = ctrl.ControlSystemSimulation(ctrl_system)
        model.stats = {'consequents': consequents}
        return model

    def predict(self, input_data: Dict) -> Dict:
        for key, value in input_data.items():
            self.base_model.input[key] = value
        self.base_model.compute()

        outputs = {}
        for cls in self.stats['consequents']:
            outputs[cls] = round(self.base_model.output[cls], 5)
        return outputs
