from typing import Dict, List

import pandas as pd

from h1st.model.predictive_model import PredictiveModel
from h1st.model.model import Model

class KSWE(PredictiveModel):
    def __init__(
        self, 
        segmentor: Model, 
        ensemble: Model, 
        sub_models: Dict[str, Model] = None,         
        sub_model: Model = None
    ):
        self.stats = {}
        self.segmentor = segmentor
        self.sub_models = sub_models
        self.sub_model_class = sub_model
        self.ensemble = ensemble

    def predict(self, input_data: Dict):
        # Remove segmentation_features from X
        if 'X_features' in self.stats:
            input_data['X'] = input_data['X'][self.stats['X_features']]

        # Generate sub_models' prediction
        sub_model_predictions = [pd.Series(sub_model.predict(input_data)['predictions']) 
                                for _, sub_model in self.sub_models.items()]
        
        # Generage ensemble's prediction
        final_predictions = self.ensemble.predict({'X': pd.concat(sub_model_predictions, axis=1)})

        return final_predictions

    def persist(self, version: str) -> None:
        self.ensemble.persist(version+'_ensemble')
        sub_model_names = []
        for name, sub_model in self.sub_models.items():
            print(version+f'_{name}')
            sub_model.persist(version+f'_{name}')
            sub_model_names.append(name)
        self.stats['sub_model_names'] = sub_model_names
        super().persist(version)

    def load_params(self, version: str) -> None:
        super().load_params(version)
        sub_model_names = self.stats['sub_model_names']
        self.ensemble.load_params(version+'_ensemble')
        sub_models = {}
        for name in sub_model_names:
            sub_model = self.sub_model_class().load_params(version+f'_{name}')
            sub_models[name] = sub_model
        self.sub_models = sub_models

    # def persist(self, version=None):
    #     for name, sub_model in self.sub_models:
    #         sub_model.persist(version)
    #     self.ensemble.persist(version)
    #     super().persist(version)

    # def load_params(self, version: str = None) -> None:
    #     self.ensemble.load_params(version)
    #     for sub_model in self.sub_models:
    #         sub_model.load_params(self.ensembler.version)
    #     super().load_params(version)

    # WIP: Switching model based on data segment
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

        