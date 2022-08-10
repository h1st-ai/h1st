from typing import NoReturn, List

import skfuzzy
from skfuzzy import control as skctrl
from skfuzzy.control.term import Term

from h1st.model.fuzzy.enums import FuzzyMembership as fm


class FuzzyRules:
    
    def add(self, rule_name, if_: Term, then_: Term) -> NoReturn:
        """
        Add a fuzzy rule. Place antecedent type variables in 'if' statement
        and place consequent type variables in 'then' statement.

        .. code-block:: python
            :caption: example

            vars = FuzzyVariables()
            vars.add(
                var_name='var1',
                var_type='antecedent',
                var_range=np.arange(0, 15+1e-5, 0.5),
                membership_funcs=[('normal', fm.GAUSSIAN, [3, 3.3]),
                                  ('abnormal', fm.TRIANGLE, [8, 15, 15])]
            )
            vars.add(
                var_name='conclusion1',
                var_type='consequent',
                var_range=np.arange(0, 10+1e-5, 0.5),
                membership_funcs=[('no', fm.TRAPEZOID, [0, 0, 4, 6]),
                                  ('yes', fm.TRAPEZOID, [4, 6, 10, 10])]
            )
            rules = FuzzyRules()
            rules.add_rule(
                'rule1',
                if_=vars.var1['abnormal'],
                then_=vars.conclusion1['yes'])
        """
        setattr(self, rule_name, skctrl.Rule(if_, then_))

    def remove(self, rule_name: str) -> NoReturn:
        if hasattr(self, rule_name):
            delattr(self, rule_name)

    def get_rules(self) -> List[skfuzzy.control.Rule]:
        return [rule for rule in self.__dict__.values()]
