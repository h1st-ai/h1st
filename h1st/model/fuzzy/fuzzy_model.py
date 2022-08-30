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
        self.fuzzy_variables = variables
        self.fuzzy_rules = rules

        if rules is None:
            self.rules = None
        else:
            self.rules = skctrl.ControlSystemSimulation(
                skctrl.ControlSystem(rules.get_rules())
            )

    def execute_rules(self, input_data: Dict) -> Dict:
        """
        Execute rules on input_data.

        .. code-block:: python
            :caption: example
            input_data = {'var1': 5, 'var2': 9}
            predictions = model.execute_rules(input_data)
        """
        if self.rules is None:
            raise ValueError(
                (
                    "Property rules is None. Please load your rules "
                    "to run this method."
                )
            )
        for key, value in input_data.items():
            self.rules.input[key] = value
        self.rules.compute()

        outputs = {}
        for cls in self.rules.ctrl.consequents:
            outputs[cls.label] = round(self.rules.output[cls.label], 5)
        return outputs

    def visualize_variables(self):
        self.fuzzy_variables.visualize()
