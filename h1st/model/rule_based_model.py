from typing import Dict
import pandas as pd
from .predictive_model import PredictiveModel


class RuleBasedModel(PredictiveModel):
    pass

class RuleBasedRegressionModel(RuleBasedModel):
    """
    Combine predictions using averaging strategy by default.
    """
    def predict(self, input_data: Dict) -> Dict:
        """
        :param input_data: a dictionary of predictions.
        :returns: a pandas series of averaged values per group of predictions.
        """
        predictions = pd.DataFrame(input_data['X']).mean(axis=1,
                                                    skipna=True,
                                                    numeric_only=True).values
        return {'predictions': predictions}

class RuleBasedClassificationModel(RuleBasedModel):
    """
    Combine predictions using majority voting by default.
    """
    def predict(self, input_data: Dict) -> Dict:
        """
        :param input_data: a dictionary of predictions.
        :returns: a pandas series of the most popular values per group of predictions.
        """
        predictions = pd.DataFrame(input_data['X']).mode(axis='columns',
                                                    numeric_only=True)[0].values
        return {'predictions': predictions}
