import logging
from typing import List, Union

import skfuzzy
from skfuzzy import control as skctrl

from h1st.model.modeler import Modeler
from h1st.model.fuzzy.fuzzy_model import FuzzyModel
from h1st.model.fuzzy.fuzzy_rules import FuzzyRules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FuzzyModeler(Modeler):
    """
    Base class for H1st Fuzzy Logic Modelers. Has capabilities that are 
    specific to FuzzyModel.

    Explain concisely something like, _FuzzyLogicModel is a RuleBasedModel. 
    You need two things to create a FuzzyLogicModel: fuzzy variables, and fuzzy rules.
    Fuzzy variables are defined using membership functions or distributions. 
    Fuzzy rules have predicates ... For more information, check out https://xxx _

    """
    def __init__(self, model_class = FuzzyModel):
        self.model_class = model_class

    def build_model(self, rules: FuzzyRules) -> FuzzyModel:

        if not isinstance(rules, FuzzyRules):
            raise ValueError((f'{type(rules)} is not instance'
                             ' of FuzzyRules'))

        # Build fuzzy logic model with fuzzy rules.
        m = self.model_class()
        m.rules = skctrl.ControlSystemSimulation(
            skctrl.ControlSystem(rules.get_fuzzy_rules()))

        return m
