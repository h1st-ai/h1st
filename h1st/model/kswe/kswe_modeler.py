import logging
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
        segmentation_features: Dict = None, 
        min_data_size: int = 50
    ):
        '''
        min_segment_size: 
            Number of data points in each segment should be larger than this value. 
            If not, ignore that segment or auto-merge it into other segment so that
            the total number data points in a merged segment is larger than min_segment_size.  
        sub_model_modeler:  
            User can use their own sub_model modeler, or use pre-built modeler, 
            such as RandomForestClassifierModeler.
        ensemble_modeler:
            User can use their own ensemble modeler, or use pre-built modeler, 
            such as MajorityVotingEnsembleModeler.        
        input_data: Dict 
            Data for training and evaluating sub_models and ensembles of KSWE. 
        segmentation_features: Dict
            Domain knowledge that will be used for segmenting data and build KSWE.        
        
        '''

        # Check if data is in correct format
        if isinstance(segmentor, CombinationSegmentor):
            if 'dataframe' not in input_data and 'json' not in input_data:
                raise KeyError('key "dataframe" or "json" is not in your input_data')     

            if 'dataframe' in input_data:
                dataframe = input_data['dataframe']
                if 'X_train' not in dataframe or 'X_test' not in dataframe:
                    raise KeyError('key "X_train" or "X_test" are not in your dataframe')            
                if 'y_train' not in dataframe or 'y_test' not in dataframe: 
                    raise KeyError('key "y_train" or "y_test" are not in your dataframe')
                if not isinstance(dataframe['X_train'], pd.DataFrame):
                    raise TypeError(f'dataframe["X_train"] should be pandas.DataFrame \
                                    but {type(dataframe["X_train"])} were given')    
                if (dataframe['X_train'].shape[0] != dataframe['y_train'].shape[0]) \
                    or (dataframe['X_test'].shape[0] != dataframe['y_test'].shape[0]):
                    raise ValueError('The length of "X" and "y" are different.')

            self.stats['segmentation_features_key'] = list(segmentation_features.keys())

            segmented_data, segmentation_logics = segmentor.process(
                input_data, 
                by=segmentation_features, 
                min_data_size=min_data_size, 
                segmentation_levels=list(range(1, len(segmentation_features)+1))
            )

            if 'json' in input_data:
                pass 
            # If X is Dict (JSON), then we need to load Image and Label information from X
            # to generate sub model predictions, and train ensemble.
            # TODO: Image/Label Loader for Detectron Model here.

            if 'dataframe' in input_data:
                X_features = list(input_data['dataframe']['X_train'].columns)
                for item in segmentation_features.keys(): X_features.remove(item)
                self.stats['X_features'] = X_features
                input_data['X_train'] = input_data['dataframe']['X_train'][X_features]
                input_data['y_train'] = input_data['dataframe']['y_train']
                input_data['X_test'] = input_data['dataframe']['X_test'][X_features]
                input_data['y_test'] = input_data['dataframe']['y_test']
        else:
            segmented_data, segmentation_logics = segmentor.process(input_data)


        # Train sub_models (TODO: make it parallelized)
        sub_models = {name: sub_model_modeler.train_model(data) \
                      for name, data in segmented_data.items()}

        # Show the evaluation results of sub_models
        for name, model in sub_models.items():
            logging.info(f'sub model {name} training resluts based on {segmented_data[name]["X_train"].shape[0]} samples: {model.metrics}')
            metrics = sub_model_modeler.evaluate_model(input_data, model)
            logging.info(f'sub model {name} test resluts based on {input_data["X_test"].shape[0]} samples: {metrics}')

        # Save segmentation_logics in self.stats. We will use this in KSWE predict method.
        self.stats['segmentation_logics'] = segmentation_logics

        # Prepare training data for Ensemble
        # Depending on the ensemble strategy, we should prepare the training data differently
        sub_model_predictions = [pd.Series(sub_model.predict({'X': input_data['X_train']})['predictions'])
                                for _, sub_model in sub_models.items()]

        # Build Ensemble
        ensemble_data = {
            'X_train': pd.concat(sub_model_predictions, axis=1),
            'y_train': input_data['y_train'],
        }
        ensemble = ensemble_modeler.build_model(ensemble_data)

        # Build KSWE
        kswe = self.model_class(
            segmentor=segmentor, 
            sub_models=sub_models, 
            ensemble=ensemble
        )

        kswe.metrics = sub_model_modeler.evaluate_model(input_data, kswe)

        # Show the evaluation results of KSWE
        print('kswe test results', kswe.metrics)
        
        # Pass stats to the model
        if self.stats is not None:
            kswe.stats = self.stats.copy()
        return kswe

