from abc import ABC, abstractmethod
import imp
from typing import Dict, List, Tuple, Union
import logging

import itertools
import numpy as np
import pandas as pd

from h1st.model.model import Model

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
