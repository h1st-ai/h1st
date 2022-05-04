from copy import deepcopy
import json
import logging
from typing import Dict, List

import pandas as pd
from sklearn.model_selection import train_test_split as sk_train_test_split

from h1st.model.modeler import Modeler
from h1st.model.rule_based_modeler import RuleBasedModeler
from .ensemble import MajorityVotingEnsemble
from .kswe import KSWE
from .segmentor import CombinationSegmentor, MaxSegmentationModeler
from .sub_model_modeler import RandomForestClassifierModeler


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
        sub_model_modeler: Modeler = RandomForestClassifierModeler(),
        ensemble_modeler: Modeler = RuleBasedModeler(model_class=MajorityVotingEnsemble),
        segmentor_modeler: Modeler = MaxSegmentationModeler(),
        segmentation_config: Dict = None, 
    ):
        '''
        :param input_data: 
            Data for training and evaluating sub_models and ensembles of KSWE.
        :param sub_model_modeler:
            User can use their own sub_model modeler, or use pre-built modeler,
            such as RandomForestClassifierModeler.
        :param ensemble_modeler:
            User can use their own ensemble modeler, or use pre-built modeler,
            such as MajorityVotingEnsembleModeler.
        :param segmentor:
            Segment data into segmented data based on segmentation_configs
        :param segmentation_config:
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

        if (bool('y_train' in input_data) ^ bool('y_test' in input_data)): 
            raise KeyError('key "y_train" or "y_test" are not in your input_data')

        if not isinstance(input_data['X_train'], pd.DataFrame):
            raise TypeError(f'input_data["X_train"] should be pandas.DataFrame \
                            but {type(input_data["X_train"])} were given')
        
        if 'y_train' in input_data and 'y_test' in input_data:
            if input_data['X_train'].shape[0] != input_data['y_train'].shape[0]:
                raise ValueError(f'The length of X_train {input_data["X_train"].shape[0]}'
                                f'and y_train {input_data["y_train"].shape[0]} are different.')
            if input_data['X_test'].shape[0] != input_data['y_test'].shape[0]:
                raise ValueError(f'The length of X_test {input_data["X_test"].shape[0]}'
                                f'and y_test {input_data["y_test"].shape[0]} are different.')                    

        segmentor = segmentor_modeler.build_model(input_data, segmentation_config)
        segmentor_output = segmentor.process({'X': input_data['X_train']})

        # Train sub_models
        sub_models = {}
        segmented_data = {}
        for name, segmented_X_train in segmentor_output['segment_data'].items():
            train_test_data = self.prepare_sub_model_train_test_data(
                name, segmented_X_train, input_data)
            
            # TODO: Move this validation into segmentor_modeler
            if ('y_train' in train_test_data) and (train_test_data['y_train'].nunique() == 1):
                logging.info(f'Skip the Training of sub_model {name} because '
                             'there is only one y class or one constant value.')
                # remove this data segment from segmentor
                del segmentor.stats['segment_info'][name]
                continue

            segmented_data[name] = train_test_data
            logging.info(f'Training sub_model {name} based on '
                         f'{segmented_X_train.shape[0]} samples')
            sub_model = sub_model_modeler.build_model(train_test_data)
            sub_model.stats['segment_info'] = segmentor_output['segment_info'][name]
            sub_models[name] = sub_model
            logging.info(f'Metrics for trained submodel {name}:\n'
                         f'{json.dumps(sub_model.metrics)}')

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
        kswe.metrics = self.evaluate_model(input_data, kswe)

        # Show the evaluation results of KSWE
        print('kswe test results:', kswe.metrics)
        return kswe

    def build_ensemble(self, ensemble_modeler, sub_models, segmented_data):
        ensemble_training_data = {}
        for name, sub_model in sub_models.items():
            data_segment = segmented_data[name]

            # Generate sub_model predictions
            sub_model_pred = sub_model.predict(
                {'X': data_segment['X_train']})['predictions']
            ensemble_training_data[name] = {
                'X_train': data_segment['X_train'],
                'y_pred_sub_model': sub_model_pred
            }

            # If y_train exists, add it in training data
            if 'y_train' in data_segment:
                ensemble_training_data[name]['y_train'] = data_segment['y_train']

        # Build Ensemble            
        ensemble = ensemble_modeler.build_model(ensemble_training_data)
        return ensemble

    def prepare_sub_model_train_test_data(self, name, X_train, input_data):
        train_test_data = {
            'X_train': X_train,
            'X_test': deepcopy(input_data['X_test']),
        }
        if 'y_test' in input_data:
            train_test_data['y_train'] = input_data['y_train'].loc[X_train.index]
            train_test_data['y_test'] = deepcopy(input_data['y_test'])
        return train_test_data
            
