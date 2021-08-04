import logging
from typing import Any, NoReturn

import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control.term import Term

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
        self.consequents = []
        self.rules = {}
        self.variables = {}
        self.membership = {
            'triangle': fuzz.trimf,
            'trapezoid': fuzz.trapmf,
            'gaussian': fuzz.gaussmf,
        }
        self.add_variables()
        self.add_rules()
        self.build()

    def add_variables(self) -> NoReturn:
        """
        Add all of your variables with add_variable function.

        .. code-block:: python
            :caption: example

            self.add_variable(
                range_=np.arange(0, 10, 0.5),
                name='sensor1',
                membership_funcs=[('normal', 'gaussian', [3, 3.3]),
                        ('abnormal', 'triangle', [8, 15, 15])],
                type_='antecedent'
            )
            self.add_variable(
                range_=np.arange(0, 10, 0.5),
                name='problem1',
                membership_funcs=[('no', 'trapezoid', [0, 0, 4, 6]),
                        ('yes', 'trapezoid', [4, 6, 10, 10])],
                type_='consequent'
            )
        """

    def add_rules(self) -> NoReturn:
        """
        Add all of your rules with the add_rule function.

        .. code-block:: python
            :caption: example

            self.add_rule(
                'rule1',
                if_=self.variables['sensor1']['abnormal'],
                then_=self.variables['problem1']['yes'])
            self.add_rule(
                'rule2',
                if_=self.variables['sensor1']['normal'],
                then_=self.variables['problem1']['no'])
        """

    def build(self) -> NoReturn:
        ctrl_system = ctrl.ControlSystem(list(self.rules.values()))
        self.css = ctrl.ControlSystemSimulation(ctrl_system)

    def add_rule(self, name, if_: Term, then_: Term) -> NoReturn:
        """
        Add a fuzzy rule. Place antecedent type variables in 'if' statement
        and place consequent type varibles in 'then' statement.

        .. code-block:: python
            :caption: example

            self.add_rule(
                'rule1',
                if_=self.variables['sensor1']['abnormal'],
                then_=self.variables['problem1']['yes'])
        """
        rule = ctrl.Rule(if_, then_)
        self.rules[name] = rule

    def remove_rule(self, name: str) -> NoReturn:
        if name in self.rules:
            del self.rules[name]           

    def add_variable(self, range_: list, name: str, membership_funcs: list, type_: str) -> NoReturn:
        """
        Add a variable with their type and membership functions.

        :param range_: the range of variable
        :param name: the name of variable
        :param membership_funcs: this is the list of tuple(membership_func_name, membership_func_type, membership_func_range)
            There are three different kinds of membership_func_type that are supported and their membership_func_range should follow the following formats.
            gaussian: [mean, sigma]
            triangle: [a, b, c] where a <= b <= c
            trapezoid: [a, b, c, d] where a <= b <= c <= d
        :param type_: the varilable type should be either consequent or antecedent

        .. code-block:: python
            :caption: example

            self.add_variable(
                range_=np.arange(0, 10, 0.5),
                name='service_quality',
                membership_funcs=[('Bad', 'gaussian', [2, 1]),
                                  ('Decent', 'triangle', [3, 5, 7]),
                                  ('Great', 'trapezoid', [6, 8, 10, 10])],
                type_='antecedent'
            )
        """
        
        if type_ == 'antecedent':
            variable = ctrl.Antecedent(range_, name)
        elif type_ == 'consequent':
            variable = ctrl.Consequent(range_, name)
            if name not in self.consequents:
                self.consequents.append(name)
        else:
            logger.warning(f'{type_} is not supported type')
            return None

        for mem_func_name, mem_func_type, mem_func_range in membership_funcs:
            if mem_func_type != 'gaussian':
                variable[mem_func_name] = self.membership[mem_func_type](
                    variable.universe, mem_func_range)
            else:
                variable[mem_func_name] = self.membership[mem_func_type](
                    variable.universe, mem_func_range[0], mem_func_range[1])

        self.variables[name] = variable

    def remove_variable(self, name: str) -> NoReturn:
        if name in self.variables:
            del self.variables[name]

    def visualize(self, variable_name: str) -> NoReturn:
        if variable_name in self.variables:
            self.variables[variable_name].view()
        else:
            logger.warning(f"{variable_name} not found")

    def predict(self, input_data: dict) -> dict:
        for key, value in input_data.items():
            self.css.input[key] = value

        self.css.compute()

        outputs = {}
        for cls in self.consequents:
            outputs[cls] = round(self.css.output[cls], 5)

        return outputs
