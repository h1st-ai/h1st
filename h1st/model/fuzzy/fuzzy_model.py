from pandas import DataFrame
from typing import Dict
from typing_extensions import Self
from skfuzzy import control as skctrl

from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.fuzzy.fuzzy_variables import FuzzyVariables
from h1st.model.fuzzy.fuzzy_rules import FuzzyRules


class FuzzyModel(RuleBasedModel):
    '''
    FuzzyModel is a RuleBasedModel that uses Fuzzy rule engine. You can create
    FuzzyModel using build_model method of FuzzyModeler. FuzzyModel has a property
    called rule_engine and it contains the core ControlSystem from skfuzzy package.
    For more information, check out https://scikit-fuzzy.github.io/scikit-fuzzy/.
    '''

    def __init__(self, variables: FuzzyVariables = None, rules: FuzzyRules = None):
        super().__init__()
        self.variables = variables
        self.rules = rules

        if rules is not None:
            self.rule_engine = skctrl.ControlSystemSimulation(
                skctrl.ControlSystem(rules.list())
            )

    def process_rules(self, input_data: Dict) -> Dict:
        '''
        Process rules on input_data.

        .. code-block:: python
            :caption: example
            input_data = {'var1': 5, 'var2': 9}
            predictions = model.process_rules({'X': input_data})
        '''
        if 'X' not in input_data:
            raise KeyError('X is not in input_data.')

        if isinstance(input_data['X'], DataFrame):
            data = input_data['X'].to_dict('records')
        elif isinstance(input_data['X'], list):
            data = input_data['X']
        else:
            data = [input_data['X']]

        predictions = map(self.process_rule, data)
        return {'predictions': DataFrame(predictions)}

    def process_rule(self, input_data: Dict) -> Dict:
        if self.rule_engine is None:
            raise ValueError(
                (
                    'Property rule_engine is None. Please load your rule_engine '
                    'to run this method.'
                )
            )

        for key, value in input_data.items():
            self.rule_engine.input[key] = value

        self.rule_engine.compute()

        outputs = {}
        for cls in self.rule_engine.ctrl.consequents:
            outputs[cls.label] = round(self.rule_engine.output[cls.label], 5)
        return outputs

    def visualize_variables(self):
        self.variables.visualize()

    def persist(self, version=None) -> str:
        '''
        persist rule_engine property and variables, and rules in rule_details.
        '''
        self.rule_details = {
            'variables': self.variables,
            'rules': self.rules,
        }
        super().persist(version)
        return version

    def load(self, version: str = None) -> Self:
        '''
        load rule_engine property and variables, and rules from rule_details.
        '''
        super().load(version)
        self.variables = self.rule_details['variables']
        self.rules = self.rule_details['rules']
        return self
