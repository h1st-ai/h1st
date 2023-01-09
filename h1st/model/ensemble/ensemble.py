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
        predictions = input_data['X'].iloc[:, 0] | input_data["X"].iloc[:, 1]
        return {'predictions': predictions}
