from typing import Any

from .model import Model


class PredictiveModel(Model):
    """
    Base class for all predictive models.
    """

    def predict(self, input_data: dict) -> dict:
        """
        Implement logic to generate prediction from data

        :params data: data for prediction
        :returns: prediction result as a dict
        """
        return self.process(input_data = input_data)
