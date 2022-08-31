import logging

from h1st.model.modeler import Modeler
from h1st.model.fuzzy.fuzzy_model import FuzzyModel
from h1st.model.fuzzy.fuzzy_variables import FuzzyVariables
from h1st.model.fuzzy.fuzzy_rules import FuzzyRules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyModeler(Modeler):
    """
    FuzzyModeler is a Modeler for FuzzyModel. Using FuzzyVariables and FuzzyRules
    FuzzyModeler builds FuzzyModel.

    """

    def __init__(self, model_class: FuzzyModel = None) -> None:
        if model_class is None:
            self.model_class = FuzzyModel
        else:
            self.model_class = model_class

    def build_model(self, variables: FuzzyVariables, rules: FuzzyRules) -> FuzzyModel:
        """
        Build FuzzyModel using variables and rules.

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
                if_term=vars.get('var1')['abnormal'],
                then_term=vars.get('conclusion1')['yes'])
            modeler = FuzzyModeler()
            model = modeler.build_model(vars, rules)
        """
        if not isinstance(rules, FuzzyRules):
            raise ValueError(f"{type(rules)} is not an instance of FuzzyRules")
        if not isinstance(variables, FuzzyVariables):
            raise ValueError(f"{type(variables)} is not an instance of FuzzyRules")

        # Build fuzzy model.
        return self.model_class(variables=variables, rules=rules)
