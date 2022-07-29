import logging
from typing import Any, Dict, NoReturn, List

import skfuzzy
from skfuzzy import control as ctrl
from skfuzzy.control.term import Term

from h1st.model.modeler import Modeler
from h1st.model.fuzzy_logic_model import FuzzyLogicModel
# from fuzzy_logic_model import FuzzyLogicModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FuzzyLogicModeler(Modeler):
    """
    Base class for H1st Fuzzy Logic Modelers. Has capabilities that are specific to FuzzyLogicModel.

    """
    def __init__(
        self, 
        fuzzy_rules: List[skfuzzy.control.Rule] = [], 
        consequents: List[str] = [], 
        model_class = FuzzyLogicModel
    ):
        self.fuzzy_rules = fuzzy_rules
        self.consequents = consequents
        self.model_class = model_class
        self.membership = {
            'triangle': skfuzzy.trimf,
            'trapezoid': skfuzzy.trapmf,
            'gaussian': skfuzzy.gaussmf,
        }
        self.rules = {}
        self.variables = {}        

    def build_model(self) -> NoReturn:
        if not self.fuzzy_rules:
            if not self.rules:
                logger.error('fuzzy rule is not provided.')
                raise ValueError('fuzzy rule is not provided.')
            self.fuzzy_rules = list(self.rules.values())
        if not self.consequents:
            logger.error('consequents is not provided.')
            raise ValueError('consequents is not provided.')

        fuzzy_logic_model = self.model_class.construct_model(
            self.fuzzy_rules,
            self.consequents
        )
        return fuzzy_logic_model

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

    def visualize_fuzzy_variables(self, fussy_model_config) -> None:
        print("=== Antecedents & Consequents ===")
        for var in self.variables.values():
            if isinstance(var, skfuzzy.control.Antecedent):
                var.view()

        for var in self.variables.values():
            if isinstance(var, skfuzzy.control.Consequent):
                var.view()
