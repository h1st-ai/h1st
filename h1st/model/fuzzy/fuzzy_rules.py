from typing import List

from skfuzzy import control as skctrl
from skfuzzy.control.term import Term


class FuzzyRules:
    def __init__(self) -> None:
        self.rules = {}

    def add(self, rule_name, if_term: Term, then_term: Term) -> None:
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
                if_term=vars.vars['var1']['abnormal'],
                then_term=vars.vars['conclusion1']['yes'])
        """
        self.rules[rule_name] = skctrl.Rule(if_term, then_term)

    def remove(self, rule_name: str) -> None:
        if rule_name in self.rules:
            self.rules.pop(rule_name)
        else:
            raise KeyError(f"rule name {rule_name} does not exist.")

    def get_rules(self) -> List[skctrl.Rule]:
        return list(self.rules.values())
