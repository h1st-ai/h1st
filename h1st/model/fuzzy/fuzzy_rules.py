from typing import NoReturn, List

import skfuzzy
from skfuzzy import control as skctrl
from skfuzzy.control.term import Term

from h1st.model.fuzzy.enums import FuzzyMembership as fm


class FuzzyRules:
    
    def add(self, rule_name, if_: Term, then_: Term): #  -> NoReturn
        """
        Add a fuzzy rule. Place antecedent type variables in 'if' statement
        and place consequent type variables in 'then' statement.

        .. code-block:: python
            :caption: example
            flr = FuzzyRules()
            flr.add_rule(
                'rule1',
                if_=flr.vars['sensor1']['abnormal'],
                then_=flr.vars['problem1']['yes'])
        """
        setattr(self, rule_name, skctrl.Rule(if_, then_))
        # self.rules[rule_name] = skctrl.Rule(if_, then_)

    def remove(self, rule_name: str) -> NoReturn:
        if hasattr(self, rule_name):
            delattr(self, rule_name)
        # self.rules.pop(name, None)

    def get_fuzzy_rules(self) -> List[skfuzzy.control.Rule]:
        return [rule for rule in self.__dict__.values()]
