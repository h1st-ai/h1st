import logging
from typing import Dict, NoReturn

import skfuzzy
from skfuzzy import control as ctrl
from skfuzzy.control.term import Term

from h1st.model.ml_model import MLModel
from h1st.model.rule_based_model import RuleBasedModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyLogicModel(RuleBasedModel):
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
        fuzzy_rules: list[skfuzzy.control.rule.Rule]
        # consequents: list
    ):
        model = cls()
        model.rules = ctrl.ControlSystemSimulation(
            ctrl.ControlSystem(fuzzy_rules))
        return model

    def execute_rules(self, input_data: Dict) -> Dict:
        for key, value in input_data.items():
            self.rules.input[key] = value
        self.rules.compute()

        outputs = {}
        for cls in self.rules.ctrl.consequents:
            outputs[cls.label] = round(self.rules.output[cls.label], 5)
        return outputs
