import json
import logging
from typing import Dict, List
from copy import deepcopy

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
        segmentation_config: Dict = None, 
    ):
        '''
        :param input_data: Dict
            Data for training and evaluating sub_models and ensembles of KSWE.
        :param sub_model_modeler:
            User can use their own sub_model modeler, or use pre-built modeler,
            such as RandomForestClassifierModeler.
        :param ensemble_modeler:
            User can use their own ensemble modeler, or use pre-built modeler,
            such as MajorityVotingEnsembleModeler.
        :param segmentor:
            Segment data into segmented data based on segmentation_configs
        :param segmentation_configs:
            Domain knowledge that will be used for segmenting data and build KSWE.
            Either a dict where each key is a column to segment on and the
            value is a list[list], each level 0 list item represents a bin and
            each level 1 list item is a class of range in that bin
            i.e.:
                {'time_of_day': [['day'], ['night']],
                'month': [['Jan', 'Feb'], ['Mar', 'Apr']],
                'depth': [[(0, 50), (75,100)], [(51, 74)]]}
            Alternatively, this can be string path to config file, see example for format.
        '''
        
        if 'X_train' not in input_data or 'X_test' not in input_data:
            raise KeyError('key "X_train" or "X_test" are not in your input_data')            
        if 'y_train' not in input_data or 'y_test' not in input_data: 
            raise KeyError('key "y_train" or "y_test" are not in your input_data')
        if not isinstance(input_data['X_train'], pd.DataFrame):
            raise TypeError(f'input_data["X_train"] should be pandas.DataFrame \
                            but {type(input_data["X_train"])} were given')    
        if (input_data['X_train'].shape[0] != input_data['y_train'].shape[0]) \
            or (input_data['X_test'].shape[0] != input_data['y_test'].shape[0]):
            raise ValueError('The length of "X" and "y" are different.')

        self.stats['segmentation_features'] = list(segmentation_config.keys())
        segmentor.stats['segmentation_config'] = segmentation_config
        segmentor_output = segmentor.process({'X': input_data['X_train']})

        sub_models = {}
        segmented_data = {}
        train_test_data = {
            'X_test': deepcopy(input_data['X_test']),
            'y_test': deepcopy(input_data['y_test'])        
        }
        for name, X_train in segmentor_output['segment_data'].items():
            y_train = input_data['y_train'].loc[X_train.index]
            train_test_data['X_train'] = X_train
            train_test_data['y_train'] = y_train
            segmented_data[name] = {'X_train': X_train, 'y_train': y_train}
            logging.info(f'Training sub_model {name} based on '
                         f'{X_train.shape[0]} samples')
            sub_model = sub_model_modeler.train_model(train_test_data)
            sub_model.stats['segment_info'] = segmentor_output['segment_info'][name]
            sub_models[name] = sub_model
            logging.info(f'Metrics for trained submodel {name}:\n'
                         f'{json.dumps(sub_model.metrics, index=4)}')

        # Save segmentation_logics in self.stats. We will use this in KSWE predict method.
        self.stats['segment_info'] = segmentor_output['segment_info']
        self.stats['segmentation_config'] = segmentation_config

        # Build ensemble
        ensemble = self.build_ensemble(
            ensemble_modeler, sub_models, segmented_data)

        # Build KSWE
        kswe = self.model_class.construct_model(
            segmentor=segmentor, 
            sub_models=sub_models, 
            ensemble=ensemble
        )
        kswe.stats.update(self.stats)
        kswe.metrics = sub_model_modeler.evaluate_model(input_data, kswe)

        # Show the evaluation results of KSWE
        print('kswe test results:', kswe.metrics)
        return kswe

    def build_ensemble(self, ensemble_modeler, sub_models, segmented_data):
        # Generate sub_model predictions
        sub_model_predictions = {
            name: sub_model.predict({'X': segmented_data[name]['X_train']})['predictions']
            for name, sub_model in sub_models.items()
        }

        # format training Y in same way
        y_train = {name: data['y_train'] for name, data in segmented_data.items()}

        # Build Ensemble
        ensemble_data = {
            'X_train': sub_model_predictions,
            'y_train': y_train,
        }
        ensemble = ensemble_modeler.build_model(ensemble_data)
        return ensemble