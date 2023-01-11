import pandas as pd
import numpy as np

from loguru import logger
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

from h1st.model.ml_modeler import MLModeler
from h1st.model.xgboost.model import XGBRegressionModel
from h1st.model.xgboost.utils import (
    extratree_rank_features,
    evaluate_regression_base_model,
)


class XGBRegressionModeler(MLModeler):
    model_class = XGBRegressionModel

    def __init__(
        self,
        result_key: str = 'result',
        max_features: int = 50,
        debug: bool = False,
        eta: float = 0.001,
        n_estimators: int = 3,
        max_depth: int = 3,
    ) -> None:
        super().__init__()
        self.stats = {
            'result_key': result_key,
            'max_features': max_features,
            'debug': debug,
            'eta': eta,
            'n_estimators': n_estimators,
            "max_depth": max_depth,
        }

    def train_base_model(self, prepared_data: dict) -> XGBRegressor:
        """
        This function can be used to build and train XGBRegression model.
        It also performs gridsearch which helps us to get optimal model
        parameters based on Mean Absolute Error.

        prepared_data requires keys: X_train, y_train, X_test, y_test
        """
        result_key = self.stats['result_key']
        max_features = self.stats['max_features']
        debug = self.stats['debug']
        logger.info(f'Fitting model {self.model_class.name} for {result_key}')

        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']

        if isinstance(y_train, pd.DataFrame) and result_key in y_train.columns:
            y_train = prepared_data['y_train'][result_key]
        elif not isinstance(y_train, (pd.Series, list, np.array)):
            raise ValueError(
                'y_train and y_test must be a DataFrame with '
                'relevant column specified via result_key or '
                '1-D Array-like'
            )

        self.stats['scaled_features'] = X_train.columns
        sc_scaler = StandardScaler()
        X_train = pd.DataFrame(
            sc_scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index,
        )

        # NaN/Inf should be handled in preprocessing but just in case
        fit_data = {
            'X_train': X_train.dropna(),
            'y_train': y_train.loc[X_train.index],
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

    def evaluate_model(self, prepared_data: dict, trained_model: XGBRegressionModel):
        """Calculate metrics"""
        fit_data = prepared_data.copy()
        result_key = self.stats['result_key']
        fit_data['y_test'] = fit_data['y_test'][result_key]
        fit_data['y_train'] = fit_data['y_train'][result_key]
        return evaluate_regression_base_model(
            fit_data,
            trained_model.base_model,
            features=trained_model.stats['selected_features'],
        )
