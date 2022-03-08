from typing import Dict, NoReturn, List
import pandas as pd
from h1st.model.predictive_model import PredictiveModel
from .oracle import Oracle
from .student import RandomForestModeler, AdaBoostModeler
from .ensemble import Ensemble


class TimeSeriesOracle(Oracle):
    def __init__(self, teacher: PredictiveModel,
                 students,
                 ensembler):
        super().__init__(teacher, students, ensembler)
        self.stats = {}

    @classmethod
    def generate_features(cls, data: Dict):
        '''
        Generate features to train the Student model.
        By default, we flatten all data points of the grouped dataframe.
        Overwrite this method to do custom featurization work.
        :param data: a dictionary of a grouped dataframe.
        '''
        df = data['data']
        ret = pd.DataFrame(df.values.reshape(1, df.shape[0] * df.shape[1]))
        return {'data': ret}

    @classmethod
    def generate_data(cls, data: Dict, teacher: PredictiveModel, stats: Dict) -> Dict:
        '''
        Generate data to train the Student model
        :param data: unlabeled data in form of {'X': pd.DataFrame}
        :returns: a dictionary of features and teacher's prediction.
        '''
        if 'X' not in data:
            raise ValueError('Please provide data in form of {\'X\': pd.DataFrame}')

        df = data['X']

        id_col = stats['id_col']
        ts_col = stats['ts_col']
        features = stats['features']

        if id_col is not None and id_col not in df.columns:
            raise ValueError(f'{id_col} does not exist')

        if ts_col is not None and ts_col not in df.columns:
            raise ValueError(f'{ts_col} does not exist')

        if id_col is not None or ts_col is not None:
            groupby_cols = []
            if id_col is not None:
                groupby_cols.append(id_col)
            if ts_col is not None:
                groupby_cols.append(ts_col)

            features_list = []
            teacher_preds = []
            for _, group_df in df.groupby(groupby_cols):
                group_df.drop(groupby_cols, axis=1, inplace=True)
                if features is not None:
                    group_df = group_df[features]

                teacher_pred = teacher.predict({'X': group_df})
                if 'predictions' not in teacher_pred:
                    raise KeyError('Teacher\'s output must contain a key named `predictions`')

                teacher_preds.append(teacher_pred['predictions'])

                features_list.append(cls.generate_features({'data': group_df})['data'])
            df_features = pd.concat(features_list).fillna(0)
        else:
            if features is not None:
                df = df[features]
            teacher_preds = teacher.predict({'X': df})['predictions']
            df_features = cls.generate_features({'data': df})

        return {'X': df_features, 'y': pd.Series(teacher_preds)}

    def predict(self, input_data: Dict) -> Dict:
        '''
        Implement logic to generate prediction from data. The TimeSeries Oracle expects the same `id_col`, `ts_col` and features provided during `build` phase to be in the provided data. It automatically process the data the same way to that of the `build` phase.
        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        '''
        return super().predict(input_data)
