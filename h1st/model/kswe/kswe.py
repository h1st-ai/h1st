from typing import Dict, List

import pandas as pd

from h1st.model.predictive_model import PredictiveModel
from h1st.model.model import Model

class KSWE(PredictiveModel):
    def __init__(self, segmentor: Model, sub_models: Dict[str, Model], ensemble: Model):
        self.segmentor = segmentor
        self.sub_models = sub_models
        self.ensemble = ensemble

    def predict(self, input_data: Dict):
        # Generate student models' predictions
        sub_model_predictions = [pd.Series(sub_model.predict(input_data)['predictions']) 
                                for _, sub_model in self.sub_models.items()]
        temp = pd.concat(sub_model_predictions, axis=1)
        print('kswe-temp.shape:', temp.shape)
        
        final_predictions = self.ensemble.predict({'X': pd.concat(sub_model_predictions, axis=1)})
        # print('kswe-final_predictions.shape:', final_predictions.shape)
        return final_predictions

    # Switching model based on data segment
    def predict2(self, input_data: Dict):
        # segment data
        segments = self.segmentor.get_segments_from_dataframe(
            input_data, 
            self.stats['segmentation_logics'], 
            self.stats['segmentation_features_key']
        )
        
        # Generate student models' predictions
        sub_model_predictions = [pd.Series(sub_model.predict(segments[name])['predictions']) 
                                for name, sub_model in self.sub_models.items()]
        final_predictions = pd.concat(sub_model_predictions, axis=0)
        return {
            'predictions': final_predictions
        }
        # print('kswe-temp.shape:', temp.shape)
        
        # final_predictions = self.ensemble.predict({'X': pd.concat(sub_model_predictions, axis=1)})
        # # print('kswe-final_predictions.shape:', final_predictions.shape)
        # return final_predictions

        