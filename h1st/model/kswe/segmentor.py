from copy import deepcopy
from typing import Dict, List, Tuple, Union
import logging

from configparser import ConfigParser
from itertools import combinations, product
import itertools
import numpy as np
import pandas as pd

from h1st.model.model import Model
from h1st.model.modeler import Modeler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CLASSES_DTYPES = [str, object, bool, pd.CategoricalDtype]


class CombinationSegmentor(Model):
    def __init__(self):
        super().__init__()

    def process(
        self, 
        input_data: Dict, 
        by: Dict, 
        segmentation_levels: List,
        min_data_size: int
    ) -> Tuple[Dict]:
        """
        Create all combination 
        :param input_data: Input data for training and inference.
        :param by: Utilize this value to segment input_data.
        :param segmentation_levels: List
            Number of features being used to create each segment. If level=1, then
            take a filter from only one featrue to create a segment. If level=2, then 
            take a filter from each feature and create a combined filter to create a 
            segment. To create a combined filter, do and operation between two filters.
            
            For example, given an above segmentation_features, if level=3, then you will
            have the following 4 segments.
                segment_1: (sepal_size, (None, 18.5)) & (sepal_aspect_ratio, (0, 0.65)) & (species, [0, 1])
                segment_2: (sepal_size, (None, 18.5)) & (sepal_aspect_ratio, (0.65, 1)) & (species, [0, 1])
                segment_3: (sepal_size, (18.5, None)) & (sepal_aspect_ratio, (0, 0.65)) & (species, [0, 1])
                segment_4: (sepal_size, (18.5, None)) & (sepal_aspect_ratio, (0.65, 1)) & (species, [0, 1])
            If level=1, then you will have the following 5 segments.
                segment_1: (sepal_aspect_ratio, (0, 0.65))
                segment_2: (sepal_aspect_ratio, (0.65, 1))
                segment_3: (sepal_size, (None, 18.5))
                segment_4: (sepal_size, (18.5, None))
                segment_5: (species, [0, 1])
        :param min_data_size: Minimum number of data points per segment. 
            If the number of data point in a segment is less than this value, 
            then, merge the small segment with other close segments.

        """
        segmentation_logics = self.create_filter_combinations(by, segmentation_levels)
        
        by_key = list(by.keys())
        if 'dataframe' in input_data:
            data = {}
            if 'X_train' in input_data['dataframe']:
                data['X'] = input_data['dataframe']['X_train']
                data['y'] = input_data['dataframe']['y_train']
            segmentation_results = self.get_segments_from_dataframe(
                data, segmentation_logics, by_key)
            if 'X_train' in input_data['dataframe']:
                for name, segmentation_result in segmentation_results.items():
                    segmentation_result['X_train'] = segmentation_result['X']
                    del segmentation_result['X']
                    segmentation_result['y_train'] = segmentation_result['y']
                    del segmentation_result['y']
        elif 'json' in input_data:
            segmentation_results = self.get_segments_from_json(input_data['json'], segmentation_logics)
        else:
            raise KeyError('input_data does not include "dataframe" or "json" key.')
        filtered_segmentation_results = self.filter_small_segments(segmentation_results, min_data_size)
        # Done: make segments from (X and Y) 
        # TODO: make get_segments work with JSON data
        # TODO: self.auto_merge_small_segments
        self.stats = {'segmentation_logics': segmentation_logics}
        return (filtered_segmentation_results, segmentation_logics)

    def auto_merge_small_segments(self, segments, min_data_size, filter_combinations):
        pass

    def create_feature_combination(self, list_of_filters, level):
        res = []
        for feature_combinaton in itertools.combinations(list_of_filters, level):
            res.append(feature_combinaton)
        return res 

    def create_combinations_with_levels(self, list_of_filters, levels):
        combinations_with_levels = []
        for level in levels:
            if len(list_of_filters) < level:
                raise ValueError(f'level ({level}) cannot be bigger than the number \
                                 of features ({len(list_of_filters)})')
            feature_combinations = self.create_feature_combination(list_of_filters, level)
            for feature_combination in feature_combinations:
                combinations = list(itertools.product(*feature_combination))
                combinations_with_levels.append((level, combinations))
        return combinations_with_levels

    def create_filter_combinations(self, by, levels=[1]):
        list_of_filters = []
        for feature, filters in by.items():
            filters_per_feature = []
            for filter in filters:
                filters_per_feature.append((feature, filter))
            list_of_filters.append(filters_per_feature)
        combinations_with_levels = self.create_combinations_with_levels(list_of_filters, levels)
        filter_combinations = {}
        idx = 0
        for level, combs in combinations_with_levels:
            for comb in combs:
                filter_combinations[f'segment_{idx}_lvl_{level}'] = list(comb)
                idx += 1
        return filter_combinations

    def get_filtered_indices_from_range(self, dataframe, feature, data_range):
        start, end = data_range
        if start and end:
            return (start <= dataframe[feature]) & (dataframe[feature] < end)
        if start:
            return (start <= dataframe[feature])
        if end:
            return (dataframe[feature] < end)
        return None

    def get_filtered_indices_from_set(self, dataframe, feature, data_set):
        return (dataframe[feature].isin(data_set))

    def get_filtered_indices(self, dataframe, feature, filter):
        if feature not in dataframe:
            raise KeyError(f'feature: {feature} is not in dataframe')
        if isinstance(filter, tuple):
            if len(filter) != 2:
                raise ValueError('Range filter should have only two values, start and end')
            filter = self.get_filtered_indices_from_range(dataframe, feature, filter)
        elif isinstance(filter, list):
            filter = self.get_filtered_indices_from_set(dataframe, feature, filter)
        else:
            raise ValueError(f'Provided filter should be either list or tuple, not {type(filter)}')    
        return filter.values

    def get_segments_from_dataframe(self, dataframe, segmentation_logics, segmentation_features_key):
        X = dataframe['X']
        X_features = list(X.columns)
        for item in segmentation_features_key: X_features.remove(item)

        segments = {}
        for segment_name, comb in segmentation_logics.items():
            list_filtered_indices = []
            for feature, filter in comb:
                filtered_indices = self.get_filtered_indices(X, feature, filter)
                list_filtered_indices.append(filtered_indices)
            segment_indices = np.column_stack(list_filtered_indices).all(axis=1)
            segments[segment_name] = {'X': X.loc[segment_indices, X_features]}
            if 'y' in dataframe:
                segments[segment_name]['y'] = dataframe['y'].loc[segment_indices]
        return segments

    def filter_small_segments(self, segments, min_data_size):
        res = {}
        for segment_name, segment in segments.items():
            if segment['X_train'].shape[0] < min_data_size:
                logger.info(f'{segment_name} has {segment["X_train"].shape[0]} number of data points,\
                            which is smaller than min_data_size: {min_data_size}')
                continue
            res[segment_name] = segment
        return res


class MaxSegmentationModel(Model):

    name = 'max_segmentation_model'

    def __init__(self):
        super().__init__()
        self.stats = {}

    def process(self, input_data: dict) -> dict:
        '''
        input dict requires key "X" contain a pandas dataframe. returns dict
        with keys "segment_info" containing dict of metadata about each segment
        and "segment_data" with a dict formatted as {segment_name: pd.DataFrame}
        '''
        X = input_data['X']

        segments = self.stats['segment_info'].keys()

        out_data = {}
        out_info = {}
        for name in segments:
            idx = self.get_segment_idx(X, name)
            if len(idx) == 0:
                continue

            out_data[name] = X.loc[idx].copy()
            out_info[name] = self.group_info(name)

        return {'segment_info': out_info,
                'segment_data': out_data}

    def group_info(self, name):
        return self.stats['segment_info'][name]

    def get_segment_idx(self, df: pd.DataFrame, segment_name: str):
        '''get indices of dataframe in segment'''
        grp = self.stats['segment_info'][segment_name]
        tmp = df.apply(lambda x: is_in_segment(x, grp), axis=1)
        return df[tmp].index.tolist()

    @classmethod
    def construct_model(cls, segments: dict):
        model = cls()
        model.stats['segment_info'] = segments
        return model


class MaxSegmentationModeler(Modeler):
    def __init__(
        self, 
        model_class = MaxSegmentationModel,
        config: Union[dict, str] = None,
    ):
        self.model_class = model_class
        if config:
            self._load_config(config)

    def _load_config(self, config: Union[dict,str]):
        if isinstance(config, str):
            self._load_config_file(config)
        elif isinstance(config, dict):
            self._load_config_dict(config)
        elif config is None:
            self.config = None
        else:
            raise TypeError('Config must be path to config file or dict of '
                            'segmentation features')

    def build_model(self, input_data: dict, config: Union[dict, str]=None):
        if config is not None:
            self._load_config(config)
            
        if self.config is None:
            raise ValueError('Must provide config or initialize with config')

        # combine X_train and X_test to create full dataframe to create groups
        # X_test is optional
        X = pd.concat([input_data['X_train'],
                       input_data.get('X_test')], axis=0)

        # Create bins for individual features
        self._create_bins(X)

        config = self.config
        min_pts = config['min_segment_size']
        seg_features = config['segmentation_features']
        max_levels = len(seg_features)

        segments = {}
        for level in np.arange(max_levels)+1:
            # Merge small segments in level 1 to make "other" segment,
            # not for level 2+
            if level == 1:
                merge_small = True
            else:
                merge_small = False

            grps = self._create_segments_for_level(X, level,
                                                   merge_small=merge_small)
            segments.update(grps)

        model = self.model_class.construct_model(segments)
        model.metrics = self.evaluate_model(input_data, model)
        return model

    def evaluate_model(self, input_data: dict, model: Model):
        X_train = input_data['X_train']
        X_test = input_data.get('X_test')
         
        train_segments = model.process({'X': X_train})['segment_data']
        if X_test is not None:
            test_segments = model.process({'X': X_test})['segment_data']
        else:
            test_segments = {}

        metrics = {}
        all_groups = set([*train_segments.keys(), *test_segments.keys()])
        for name in all_groups:
            train = train_segments.get(name)
            test = test_segments.get(name)

            if train is None:
                n_train = 0
            else:
                n_train = train.shape[0]

            if test is None:
                n_test = 0
            else:
                n_test = test.shape[0]

            metrics[name] = {'train_pts_in_segment': n_train,
                             'test_pts_in_segment': n_test}

        return metrics

    def _create_segments_for_level(self, labels: pd.DataFrame, level: int,
                                  merge_small=False):
        '''If merge_small is true then small groups are merged. Otherwise they
        are cut. For level>1, its probably best to cut them, for level==1 you
        should merge them for complete data coverage'''
        config = self.config
        min_pts = config['min_segment_size']
        seg_features = config['segmentation_features']

        features = [x['feature'] for x in seg_features]
        bins = [x['bins'] for x in seg_features]
        bin_types = [x['bin_type'] for x in seg_features]

        feat_grps = combinations(features, level)
        good_groups = []
        small_groups = []
        for fgrp in feat_grps:
            bin_grps = product(*[bins[features.index(x)] for x in fgrp])
            for bgrp in bin_grps:
                tmp = {
                    'features': list(fgrp),
                    'bins': list(bgrp),
                    'bin_types': [bin_types[features.index(x)] for x in fgrp],
                    'level': int(level),
                }
                in_grp = labels.apply(
                    lambda x: is_in_segment(x, tmp), axis=1
                )
                tmp['n_pts'] = sum(in_grp)
                if tmp['n_pts'] < min_pts:
                    small_groups.append(tmp)
                else:
                    good_groups.append(tmp)

        # Merge small groups
        if merge_small:
            other_group = self.merge_groups(small_groups)
            good_groups.extend(other_group)

        # Name groups
        out_segments = {}
        for i, grp in enumerate(good_groups):
            group_name = f'lvl_{level}-group_{i}'
            out_segments[group_name] = grp

        return out_segments

    def _create_bins(self, labels: pd.DataFrame):
        config = deepcopy(self.config)
        min_pts = config['min_segment_size']
        seg_features = deepcopy(config['segmentation_features'])

        for seg in seg_features:
            if 'bins' in seg.keys():
                continue

            feat = seg['feature']
            n_bins = seg.get('n_bins')
            bins = get_bins(labels[feat], n_bins=n_bins)
            good_bins = []
            small_bins = []
            for bin_ in bins:
                if type(bin_[0]) in CLASSES_DTYPES:
                    bin_type = 'classes'
                else:
                    bin_type = 'edges'

                n_pts = sum(
                    labels[feat].apply(
                        lambda x: is_in_bin(x, bin_, bin_type)
                    )
                )
                if n_pts >= min_pts:
                    good_bins.append(bin_)
                else:
                    small_bins.append(bin_)

            # TODO: More intelligent way to combine small bins
            other_bin = []
            for x in small_bins:
                other_bin.extend(x)

            if len(other_bin) > 0:
                good_bins.append(other_bin)

            seg['bins'] = good_bins
            seg['bin_type'] = bin_type
            seg['n_bins'] = len(good_bins)

        config['segmentation_features'] = seg_features
        self.config = config

    def merge_groups(self, groups):
        '''merge groups on same features'''
        if len(groups) == 1:
            return groups

        # if all groups have different feature-sets return
        feats = [x['features'] for x in groups]
        unique_feats = unique_lists(*feats)
        if len(unique_feats) == len(feats):
            return groups

        new_grps = {}
        for grp in groups:
            idx = [i for i,x in enumerate(unique_feats)
                   if unordered_list_equal(x, grp['features'])][0]
            base = new_grps.get(idx)
            if base is None:
                new_grps[idx] = grp
                continue

            for feat_, bin_, type_ in zip(grp['features'], grp['bins'],
                                          grp['bin_types']):
                idx2 = base['features'].index(feat_)
                base['bins'][idx2].extend(bin_)

        return list(new_grps.values())

    def _load_config_file(self, config_file: str):
        '''
        config must have sections:
            - defaults: min_segment_size (int), features (list[str])
        optional sections:
            - custom_bins:
                key matches features,
                list[list[str|int]] OR list[list[tuple]]
            - n_bins: key matches features, int

        A given feature can EITHER have custom_bins OR n_bins or neither,
        if custom_bins then those are used, if n_bins then n_bins or less are
        created depending on min_segment_size, if neither then bins are
        automatically created
        '''
        config = ConfigParser()
        config.read(config_file)
        feats = eval(config['defaults']['features'])
        config_dict = {
            'min_segment_size': int(config['defaults']['min_segment_size']),
            'features': feats,
        }
        if config.has_section('custom_bins'):
            tmp = {k: eval(v) for k,v in config['custom_bins'].items()}
            config_dict['custom_bins'] = tmp

        if config.has_section('n_bins'):
            tmp = {k: int(v) for k,v in config['n_bins'].items()}
            config_dict['n_bins'] = tmp

        self._load_config_dict(config_dict)

    def _load_config_dict(self, config: dict):
        '''
        dict must have keys:
            - min_segment_size: int
            - features: list[str]
        optional keys are:
            - custom_bins: dict with keys matching feature in features and
              values as list[list[str|int]] or list[list[tuple]]
        '''
        feats = config['features']
        min_pts = config['min_segment_size']
        segments = [{'feature': x} for x in feats]
        if 'custom_bins' in config.keys():
            for key, bins in config['custom_bins'].items():
                if key not in feats:
                    continue

                idx = feats.index(key)
                seg = segments[idx]
                seg['bins'] = bins
                seg['n_bins'] = len(bins)
                if type(bins[0][0]) == tuple:
                    seg['bin_type'] = 'edges'
                else:
                    seg['bin_type'] = 'classes'

        if 'n_bins' in config.keys():
            for key, n_bins in config['n_bins'].items():
                if key not in feats:
                    continue

                idx = feats.index(key)
                if 'bins' in segments[idx].keys():
                    continue

                segments[idx]['n_bins'] = n_bins

        config_dict = {
            'segmentation_features': segments,
            'min_segment_size': min_pts
        }
        self.config = config_dict


def is_in_bin(x, bin_, type_):
    '''is value in bin'''
    if type_=='classes':
        return (x in bin_)
    elif type_=='edges':
        for rng in bin_:
            if rng[0]<=x<=rng[1]:
                return True

        return False
    else:
        raise ValueError('invalid bin type')


def is_in_segment(row, segment: dict):
    '''is data row in segment'''
    feats = segment['features']
    bins = segment['bins']
    types = segment['bin_types']
    if all([is_in_bin(row[feat_], bin_, type_)
            for feat_, bin_, type_ in zip(feats, bins, types)]):
        return True

    return False


def get_bins(dat: pd.Series, n_bins=None):
    # If data is categorical or boolean each category is a bin
    # If data is a number split into even bins
    if dat.dtype in CLASSES_DTYPES:
        groups = list(dat.unique())
        bins = [[x] for x in groups]
        return bins

    if n_bins is not None:
        _, edges = np.histogram(dat, bins=n_bins)
    else:
        _, edges = np.histogram(dat)

    bins = [[(edges[i].item(), edges[i+1].item())]
            for i in range(len(edges)-2)]
    return bins


def unique_lists(*args):
    unique = []
    for a in args:
        if len(unique) == 0:
            unique.append(a)
            continue

        to_add = True
        for b in unique:
            if unordered_list_equal(a,b):
                to_add = False

        if to_add:
            unique.append(a)

    return unique


def unordered_list_equal(a,b):
    return (all([x in a for x in b]) and all([x in b for x in a]))

