from typing import Dict

from h1st.model.model import Model


class PredictiveModel(Model):
    """
    Base class for all predictive models.
    """

    data_key = 'X'
    output_key = 'predictions'

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data is input data for prediction
        :returns: a dictionary with key `predictions` containing the predictions
        """
        return {"predictions": None}

    def process(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data
        """
        return self.predict(input_data=input_data)
