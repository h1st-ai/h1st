import pandas as pd
import numpy as np

from loguru import logger
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

from h1st.model.ml_modeler import MLModeler
from h1st.model.xgboost.model import XGBRegressionModel
from h1st.model.xgboost.utils import (
    xgb_grid_search,
    extratree_rank_features,
    evaluate_regression_base_model,
)


class XGBRegressionModeler(MLModeler):
    model_class = XGBRegressionModel

    def __init__(
        self,
        result_key: str = 'result',
        max_features: int = 50,
        eta: float = 0.001,
        n_estimators: int = 3,
        max_depth: int = 3,
        debug=False
    ) -> None:
        super().__init__()
        self.stats = {
            'result_key': result_key,
            'max_features': max_features,
            'eta': eta,
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'debug': debug,
        }

    def train_base_model(self, input_data: dict) -> XGBRegressor:
        """
        This function can be used to build and train XGBRegression model.
        It also performs gridsearch which helps us to get optimal model
        parameters based on Mean Absolute Error.

        prepared_data requires keys: X_train, y_train, X_test, y_test
        """
        result_key = self.stats['result_key']
        max_features = self.stats['max_features']
        logger.info(f'Fitting model {self.model_class.name} for {result_key}')

        prepared_data = self.prepare_data(input_data)
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test']
            y_test = prepared_data['y_test']
        else:
            X_test = None
            y_test = None

        self.stats['scaled_features'] = X_train.columns
        sc_scaler = StandardScaler()
        X_train = pd.DataFrame(
            sc_scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index,
        )
        if X_test is not None:
            X_test = pd.DataFrame(
                sc_scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index,
            )

        fit_data = {
            'X_train': X_train,
            'y_train': y_train,
        }

        ranked_features, feature_importance = extratree_rank_features(
            fit_data['X_train'], fit_data['y_train'].values
        )

        # Keep the top N features
        features = ranked_features[:max_features]

        self.stats.update(
            {
                'ranked_features': ranked_features,
                'feature_importance': feature_importance,
                'selected_features': features,
                'scaling_model': sc_scaler,
            }
        )

        fit_data['X_train'] = fit_data['X_train'][features]
        if X_test is not None:
            fit_data['X_test'] = X_test[features]
            fit_data['y_test'] = y_test
            logger.info('Found test data, grid searching to '
                        'optimize hyperparameters.')
            hyperparams = xgb_grid_search(fit_data, debug=self.stats['debug'])
            max_depth, n_estimators, eta = hyperparams
            logger.info(f'Best hyperparmeters found:\n'
                        f'n_estimators: {n_estimators}\n'
                        f'max_depth: {max_depth}\n'
                        f'eta: {eta}\n'
                        f'Replacing passed hyperparameters.'
                        )
            self.stats.update({
                'max_depth': max_depth,
                'n_estimators': n_estimators,
                'eta': eta
            })


        max_depth = self.stats['max_depth']
        eta = self.stats['eta']
        n_estimators = self.stats['n_estimators']

        # Model Initialization using the above best parameters
        model = XGBRegressor(
            max_depth=max_depth,
            n_estimators=n_estimators,
            eta=eta,
            seed=42,
            verbosity=0,
        )
        # Model Training
        model.fit(fit_data['X_train'], fit_data['y_train'])

        # Calculating Model stats
        self.stats.update(
            {
                'total_training_points': fit_data['X_train'].shape[0],
            }
        )
        return model

    def prepare_data(self, prepared_data: dict):
        fit_data = prepared_data.copy()
        # NaN/Inf should be handled in preprocessing but just in case
        X_train = prepared_data['X_train'].dropna()
        y_train = prepared_data['y_train'].loc[X_train.index]
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test'].dropna()
            y_test = prepared_data['y_test'].loc[X_test.index]
        else:
            X_test = None
            y_test = None

        if isinstance(y_train, pd.DataFrame) and result_key in y_train.columns:
            y_train = prepared_data['y_train'][result_key]
            if y_test is not None:
                y_test = prepared_data['y_test'][result_key]
        elif not isinstance(y_train, (pd.Series, list, np.array)):
            raise ValueError(
                'y_train and y_test must be a DataFrame with '
                'relevant column specified via result_key or '
                '1-D Array-like'
            )

        fit_data = {
            'X_train': X_train,
            'y_train': y_train
        }
        if X_test is not None:
            fit_data['X_test'] = X_test
            fit_data['y_test'] = y_test

        return fit_data

    def evaluate_model(self, input_data, trained_model):
        """ Calculate metrics """
        fit_data = self.prepared_data(input_data)
        return evaluate_regression_base_model(
            fit_data,
            trained_model.base_model,
            features=trained_model.stats['selected_features']
        )

