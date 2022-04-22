from typing import Dict, List

from sklearn.model_selection import train_test_split as sk_train_test_split
import pandas as pd

from h1st.model.model import Model
from h1st.model.modeler import Modeler
from h1st.model.ml_modeler import MLModeler
from segmentor import CombinationSegmentor
from kswe import KSWE
from sub_model_modeler import RandomForestClassifierModeler
from ensemble import MajorityVotingEnsemble


class KSWEModeler(Modeler):
    def __init__(self, model_class=KSWE):
        self.model_class = model_class
        self.stats = {}

    def train_test_split(self, dataframe, test_size=0.4) -> Dict:
        sk_train_test_split(dataframe, test_size)
        pass 

    def build_model(
        self,
        input_data: Dict, 
        sub_model_modeler: MLModeler,
        ensemble_modeler: Modeler,
        segmentor: Model = CombinationSegmentor(),         
        segmentation_levels: list = None,
        segmentation_features: Dict = None, 
        min_data_size: int = 50
    ):
        # Check if data is in correct format
        if isinstance(segmentor, CombinationSegmentor):
            if 'dataframe' not in input_data and 'json' not in input_data:
                raise KeyError('key "dataframe" or "json" is not in your input_data')     

            if 'dataframe' in input_data:
                dataframe = input_data['dataframe']
                if 'X' not in dataframe:
                    raise KeyError('key "X" is not in your dataframe')            
                if 'y' not in dataframe:
                    raise KeyError('key "y" is not in your dataframe')
                if not isinstance(dataframe['X'], pd.DataFrame):
                    raise TypeError(f'dataframe["X"] should be pandas.DataFrame \
                                    but {type(dataframe["X"])} were given')    
                if dataframe['X'].shape[0] != dataframe['y'].shape[0]:
                    raise ValueError('The length of "X" and "y" are different.')

            segmented_data, segmentation_logics = segmentor.process(
                input_data, 
                by=segmentation_features, 
                min_data_size=min_data_size, 
                levels=list(range(1, len(segmentation_features)+1))
            )
            if 'json' in input_data:
                pass 
            # If X is Dict (JSON), then we need to load Image and Label information from X
            # to generate sub model predictions, and train ensemble.
            # TODO: Image/Label Loader for Detectron Model here.

            if 'dataframe' in input_data:
                X_features = list(input_data['dataframe']['X'].columns)
                for item in segmentation_features.keys(): X_features.remove(item)
                input_data['X'] = input_data['dataframe']['X'][X_features]
                input_data['y'] = input_data['dataframe']['y']
        else:
            segmented_data, segmentation_logics = segmentor.process(input_data)

        # Build sub_models (TODO: make it parallelized)
        sub_models = {name: sub_model_modeler.train_model(data) \
                      for name, data in segmented_data.items()}

        # Show the evaluation results of sub_models
        for name, model in sub_models.items():
            print(name, segmentation_logics[name], model.metrics)

        # Save segmentation_logics in self.stats. We will use this in KSWE predict method.
        self.stats['segmentation_logics'] = segmentation_logics

        # Prepare training data for Ensemble
        # Depending on the ensemble strategy, we should prepare the training data differently
        sub_model_predictions = [pd.Series(sub_model.predict(input_data)['predictions']) 
                                for _, sub_model in sub_models.items()]
        
        # Build Ensemble
        ensemble_data = {
            'X': pd.concat(sub_model_predictions, axis=1),
            'y': input_data['y'],
        }
        ensemble = ensemble_modeler.build_model(ensemble_data)

        # Build KSWE
        kswe = self.model_class(segmentor, sub_models, ensemble)
        kswe.metrics = sub_model_modeler.evaluate_model(input_data, kswe)

        # Show the evaluation results of KSWE
        print('kswe evaluation results', kswe.metrics)
        
        # Pass stats to the model
        if self.stats is not None:
            kswe.stats = self.stats.copy()
        return kswe

