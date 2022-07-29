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
    Base class for H1st Fuzzy Logic Modelers. Has capabilities that are 
    specific to FuzzyLogicModel.

    """
    def __init__(self, model_class = FuzzyLogicModel):
        self.model_class = model_class

    def build_model(self, fuzzy_rules: List[skfuzzy.control.Rule]) -> FuzzyLogicModel:
        # if not self.:
        #     if not self.rules:
        #         logger.error('fuzzy rule is not provided.')
        #         raise ValueError('fuzzy rule is not provided.')
        #     self.fuzzy_rules = list(self.rules.values())
        # if not self.consequents:
        #     logger.error('consequents is not provided.')
        #     raise ValueError('consequents is not provided.')

        fuzzy_logic_model = self.model_class.construct_model(
            fuzzy_rules
            # self.consequents
        )
        return fuzzy_logic_model

    def build_fuzzy_rules_from_knowledge(self, ):
        pass