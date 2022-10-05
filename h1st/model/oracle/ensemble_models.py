from pandas import DataFrame

from h1st.model.ml_model import MLModel
from h1st.model.predictive_model import PredictiveModel


class MajorityVotingEnsembleModel(PredictiveModel):
    '''
    Ensemble Model in Oracle framework
    '''

    def predict(self, input_data: dict) -> dict:
        '''
        Combine output of teacher and students using majority voting by default. In case
        when majority vote cannot be applied, use teacher's output as the final output.
        Inherit and override this method to use your custom combining approach.
        :param input_data: dictionary with `X` key and input data
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        predictions = input_data['x'].mode(axis='columns', numeric_only=True)[0]
        return {'predictions': predictions}


class MLPEnsembleModel(MLModel):
    def predict(self, input_data: dict) -> dict:
        if isinstance(input_data['x'], DataFrame):
            x = input_data['X'].values
        else:
            x = input_data['X']

        x = self.stats['scaler'].transform(input_data['x'])
        y = self.base_model.predict(x)
        return {'predictions': y}
