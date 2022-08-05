import logging
from typing import List, Union

import skfuzzy
from skfuzzy import control as skctrl

from h1st.model.modeler import Modeler
from h1st.model.fuzzy.fuzzy_logic_model import FuzzyLogicModel
from h1st.model.fuzzy.fuzzy_logic_rules import FuzzyLogicRules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FuzzyLogicModeler(Modeler):
    """
    Base class for H1st Fuzzy Logic Modelers. Has capabilities that are 
    specific to FuzzyLogicModel.

    """
    def __init__(self, model_class = FuzzyLogicModel):
        self.model_class = model_class

    def build_skfuzzy_control_system(self, fuzzy_rules: FuzzyLogicRules):
        return skctrl.ControlSystemSimulation(
            skctrl.ControlSystem(fuzzy_rules.get_fuzzy_rules()))

    def build_model(self, fuzzy_logic_rules: FuzzyLogicRules) -> FuzzyLogicModel:

        if not isinstance(fuzzy_logic_rules, FuzzyLogicRules):
            raise ValueError((f'{type(fuzzy_logic_rules)} is not instance'
                             ' of FuzzyLogicRules'))

        # Build fuzzy logic model with fuzzy rules.
        fuzzy_logic_model = self.model_class()
        fuzzy_logic_model.rules = self.build_skfuzzy_control_system(fuzzy_logic_rules)

        return fuzzy_logic_model
