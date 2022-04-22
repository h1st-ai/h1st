from typing import Dict
import pandas as pd
from h1st.model.predictive_model import PredictiveModel
from h1st.model.rule_based_modeler import RuleBasedModeler

class Ensemble(PredictiveModel):
    """
    Ensembler Model in Segmented World Ensemble framework
    """
    def predict(self, input_data: Dict) -> Dict:
        return {'predictions': None}


class MajorityVotingEnsemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """
    def vote_on(self, df_sub_model_predictions):
        '''
        Do majority voting on sub models' prediction to get the final classificiation result

        :param df_sub_model_predictions: Pandas DataFrame including sum model's prediction in each column
        :returns: a dictionary with key `predictions` and value containing the predictions in numpy array
        '''
        if df_sub_model_predictions.shape[1] == 1:
            predictions = df_sub_model_predictions.iloc[:, 0]
        else:
            predictions = df_sub_model_predictions.mode(axis='columns', numeric_only=True)[0]

        return predictions

    def predict(self, input_data: Dict) -> Dict:
        # df_sub_model_predictions = pd.DataFrame(
        #     {f'sub_model_pred_{i}': sub_model_pred \
        #         for i, sub_model_pred in enumerate(input_data['sub_model_predictions'])}
        # )
        return {
            'predictions': self.vote_on(input_data['X'])
        }
