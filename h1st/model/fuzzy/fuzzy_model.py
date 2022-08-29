import logging
from typing import Dict

import pandas as pd

from h1st.model.rule_based_model import RuleBasedModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyModel(RuleBasedModel):
    """
    This FuzzyModel is a RuleBasedModel. You can create FuzzyModel using 
    build_model method of FuzzyModeler. FuzzyModel has a property called
    rules and it contains the core ControlSystem from skfuzzy package. 
    For more information, check out https://pythonhosted.org/scikit-fuzzy/.

    """
    def __init__(self):
        super().__init__()

    def execute_rules_pointwise(self, input_data: Dict) -> Dict:
        if self.rules is None:
            raise ValueError(('Property rules is None. Please load your rules '
                              'to run this method.'))
        for key, value in input_data.items():
            self.rules.input[key] = value
        self.rules.compute()

        outputs = {}
        for cls in self.rules.ctrl.consequents:
            outputs[cls.label] = round(self.rules.output[cls.label], 3)
        return outputs

    def execute_rules(self, input_data: Dict) -> Dict:
        df = input_data['x']
        temp = map(self.execute_rules_pointwise, df.to_dict('records'))
        # predictions = list(map(lambda x: list(x.values()), temp))
        # predictions = list(map(lambda x: 1 if list(x.values())[0] > 0.6 else 0, temp))
        return {'predictions': pd.DataFrame(temp)}

