from h1st.model.predictive_model import PredictiveModel

class Ensemble(PredictiveModel):
    """
    Base ensemble class.
    """


class LogicalOREnsemble(PredictiveModel):
    def predict(self, input_data: dict) -> dict:
        '''
        Combine output of teacher and students using majority voting by default. In case
        when majority vote cannot be applied, use teacher's output as the final output.
        Inherit and override this method to use your custom combining approach.
        :param input_data: dictionary with `X` key and input data
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        X = input_data[self.data_key]
        #predictions = input_data['X'].iloc[:, 0] | input_data["X"].iloc[:, 1]
        predictions = X.any(axis='columns').astype(int)
        return {self.output_key: predictions}


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
        predictions = input_data[self.data_key].mode(
            axis='columns', numeric_only=True)[0]
        return {self.output_key: predictions}
