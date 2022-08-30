import logging
from typing import Dict
from skfuzzy import control as skctrl

from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.fuzzy.fuzzy_variables import FuzzyVariables
from h1st.model.fuzzy.fuzzy_rules import FuzzyRules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyModel(RuleBasedModel):
    """
    FuzzyModel is a RuleBasedModel. You can create FuzzyModel using
    build_model method of FuzzyModeler. FuzzyModel has a property called
    rules and it contains the core ControlSystem from skfuzzy package.
    For more information, check out https://scikit-fuzzy.github.io/scikit-fuzzy/.
    """

    def __init__(self, variables: FuzzyVariables = None, rules: FuzzyRules = None):
        super().__init__()
        self.variables = variables
        self.rules = rules

        if rules is None:
            self.fuzzy_engine = None
        else:
            self.fuzzy_engine = skctrl.ControlSystemSimulation(
                skctrl.ControlSystem(list(rules.rules.values()))
            )

    def process_rules(self, input_data: Dict) -> Dict:
        """
        Execute rules on input_data.

        .. code-block:: python
            :caption: example
            input_data = {'var1': 5, 'var2': 9}
            predictions = model.process_rules(input_data)
        """
        if self.fuzzy_engine is None:
            raise ValueError(
                (
                    "Property fuzzy_engine is None. Please load your fuzzy_engine "
                    "to run this method."
                )
            )
        for key, value in input_data.items():
            self.fuzzy_engine.input[key] = value
        self.fuzzy_engine.compute()

        outputs = {}
        for cls in self.fuzzy_engine.ctrl.consequents:
            outputs[cls.label] = round(self.fuzzy_engine.output[cls.label], 5)
        return outputs

    def visualize_variables(self):
        self.variables.visualize()

    def persist(self, version=None):
        """
        persist all pieces of oracle and store versions & classes
        """
        self.rule_details = {
            "variables": self.variables,
            "rules": self.rules,
            "rule_engine": self.fuzzy_engine,
        }
        super().persist(version)
        return version

    def load(self, version: str = None) -> None:
        """
        load all pieces of oracle, return complete oracle
        """
        super().load(version)
        self.variables = self.rule_details["variables"]
        self.rules = self.rule_details["rules"]
        self.fuzzy_engine = self.rule_details["rule_engine"]
        return self
