from typing import Dict
from abc import ABC, abstractclassmethod

from .model import Model


class PredictiveModel(Model, ABC):
    """
    Base class for all predictive models.
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data: data for prediction
        :returns: a dictionary with key `predictions` containing the predictions
        """
        return self.process(input_data=input_data)
