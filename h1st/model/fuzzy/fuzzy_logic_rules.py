import logging
from typing import NoReturn

import skfuzzy
from skfuzzy import control as skctrl
from skfuzzy.control.term import Term

from h1st.model.fuzzy.enums import FuzzyMembership as fm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyLogicRules:
    def __init__(self) -> None:
        self.membership = {
            fm.TRIANGLE: skfuzzy.trimf,
            fm.TRAPEZOID: skfuzzy.trapmf,
            fm.GAUSSIAN: skfuzzy.gaussmf,
        }   
        self.vars = {}
        self.rules = {}

    def add_rule(self, name, if_: Term, then_: Term): #  -> NoReturn
        """
        Add a fuzzy rule. Place antecedent type variables in 'if' statement
        and place consequent type variables in 'then' statement.

        .. code-block:: python
            :caption: example
            flr = FuzzyLogicRules()
            flr.add_rule(
                'rule1',
                if_=flr.vars['sensor1']['abnormal'],
                then_=flr.vars['problem1']['yes'])
        """
        self.rules[name] = skctrl.Rule(if_, then_)

    def remove_rule(self, name: str) -> NoReturn:
        self.rules.pop(name, None)

    def add_variable(self, range_: list, name: str, membership_funcs: list, type_: str): #  -> NoReturn
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
            flr = FuzzyLogicRules()
            flr.add_variable(
                range_=np.arange(0, 10, 0.5),
                name='service_quality',
                membership_funcs=[('Bad', 'gaussian', [2, 1]),
                                  ('Decent', 'triangle', [3, 5, 7]),
                                  ('Great', 'trapezoid', [6, 8, 10, 10])],
                type_='antecedent'
            )
        """

        if type_ == 'antecedent':
            variable = skctrl.Antecedent(range_, name)
        elif type_ == 'consequent':
            variable = skctrl.Consequent(range_, name)
        else:
            logger.error(f'{type_} is not supported type')
            raise ValueError(f'{type_} is not supported type')

        for mem_func_name, mem_func_type, mem_func_range in membership_funcs:
            if mem_func_type != fm.GAUSSIAN:
                variable[mem_func_name] = self.membership[mem_func_type](
                    variable.universe, mem_func_range)
            else:
                variable[mem_func_name] = self.membership[mem_func_type](
                    variable.universe, mem_func_range[0], mem_func_range[1])

        self.vars[name] = variable

    def remove_variable(self, name: str) -> NoReturn:
        if name in self.vars:
            del self.vars[name]

    def visualize_fuzzy_variables(self, fussy_model_config) -> None:
        print("=== Antecedents & Consequents ===")
        for var in self.vars.values():
            if isinstance(var, skfuzzy.control.Antecedent):
                var.view()

        for var in self.vars.values():
            if isinstance(var, skfuzzy.control.Consequent):
                var.view()

    def get_fuzzy_rules(self) -> skfuzzy.control.Rule:
        return [rule for rule in self.rules.values()]
