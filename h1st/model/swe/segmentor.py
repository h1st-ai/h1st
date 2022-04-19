from abc import ABC, abstractmethod
import imp
from typing import Dict, List
import logging

import itertools
import numpy as np

from h1st.model.model import Model

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Segmentor(Model, ABC):
    @abstractmethod
    def segment(self, input_data: Dict, by: Dict) -> Dict:
        """
        Segment input_data using by parameter. User need to implement this method.
        :param input_data: Input data for training and inference.
        :param by: Utilize this value to segment input_data.
        """

        return input_data

    def process(self, input_data: Dict, by: Dict) -> Dict:
        return self.segment(input_data, by)


class CombinationSegmentor(Model):
    def segment(self, dataframe, by: Dict, min_data_size: int) -> Dict:
        """
        Create all combination 
        :param input_data: Input data for training and inference.
        :param by: Utilize this value to segment input_data.
        :param min_data_size: Minimum number of data points per segment. 
            If the number of data point in a segment is less than this value, 
            then, merge the small segment with other close segments.
        """
        
        filter_combinations = self.create_filter_combinations(by, levels=[1])
        segments = self.get_segments(dataframe, filter_combinations)
        segments = self.filter_small_segments(segments, min_data_size)
        # TODO: self.auto_merge_small_segments
        return segments

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
                filter_combinations[f'group_{idx}_lvl_{level}'] = comb
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

    def get_segments(self, dataframe, combinations):
        segments = {}
        for group_name, comb in combinations.items():
            list_filtered_indices = []
            for feature, filter in comb:
                # segment = get_segment(segment, feature, filter)
                filtered_indices = self.get_filtered_indices(dataframe, feature, filter)
                list_filtered_indices.append(filtered_indices)
            segment_indices = np.column_stack(list_filtered_indices).all(axis=1)
            segments[group_name] = dataframe[segment_indices]
            
        return segments

    def filter_small_segments(self, segments, min_data_size):
        res = {}
        print(segments)
        for group_name, segment in segments.items():
            if segment.shape[0] < min_data_size:
                logger.info(f'{group_name} has {segment.shape[0]} number of data points,\
                            which is smaller than min_data_size: {min_data_size}')
                continue
            res[group_name] = segment
        return res

# TODO: Given x, which model should we use ? or give more weights ? 
# TODO: Need to develop a method called find_group(x) -> group_name

