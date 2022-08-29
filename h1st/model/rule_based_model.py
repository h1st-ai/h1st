from typing import Dict, Any
import pandas as pd
from h1st.model.predictive_model import PredictiveModel

class RuleBasedModel(PredictiveModel):

    @property
    def rules(self) -> Any:
        return getattr(self, "__rules", None)
    
    @rules.setter
    def rules(self, value):
        setattr(self, "__rules", value)

    def execute_rules(self, input_data: Dict) -> Dict:
        return input_data

    def predict(self, input_data: Dict) -> Dict:
        return self.execute_rules(input_data)


class RuleBasedRegressionModel(RuleBasedModel):
    """
    Combine predictions using averaging strategy by default.
    """
    def predict(self, input_data: Dict) -> Dict:
        """
        :param input_data: a dictionary of predictions.
        :returns: a pandas series of averaged values per group of predictions.
        """
        predictions = pd.DataFrame(input_data['x']).mean(axis=1,
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
        predictions = pd.DataFrame(input_data['x']).mode(axis='columns',
                                                    numeric_only=True)[0].values
        return {'predictions': predictions}
