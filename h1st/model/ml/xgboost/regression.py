import pandas as pd
import numpy as np
import pytz
from loguru import logger
from typing import Any, Dict

from datetime import datetime
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from h1st.model.model import Model
from h1st.model.ml.xgboost.utils import extratree_rank_features, evaluate_regression_base_model


class XGBRegressionModel(Model):

    input_key = 'X'
    output_key = 'predictions'
    name = 'XGBRegression'

    def __init__(
        self,
        result_key: str = 'result',
        max_features: int = 50,
        eta: float = 0.001,
        n_estimators: int = 5,
        max_depth: int = 3,
        debug: bool = False,
    ) -> None:

        super().__init__()
        self.stats = {
            'result_key': result_key,
            'max_features': int(max_features),
            'eta': eta,
            'n_estimators': int(n_estimators),
            'max_depth': int(max_depth),
            'debug': debug,
        }

    def predict(self, input_data: dict) -> dict:
        X = input_data[self.input_key]
        output_col = self.stats['result_key']
        results = {}
        # Saving prediction time
        now = pytz.UTC.localize(datetime.utcnow())
        results['prediction_time'] = now.isoformat()
        # Scaling the input data
        scaler = self.stats['scaling_model']
        features = self.stats['scaled_features']
        selected_features = self.stats['selected_features']
        X_prime = pd.DataFrame(scaler.transform(X[features]), columns=features)
        X_prime = X_prime[selected_features]

        # Model Prediction
        pred = self.base_model.predict(X_prime)
        results[self.output_key] = pd.DataFrame(
            pred, columns=[output_col], index=X.index
        )
        return results
    

    # TRAINING MODEL
    def prepare_data(self, prepared_data: dict):
        result_key = self.stats['result_key']

        # NaN/Inf should be handled in preprocessing but just in case
        X_train = prepared_data['X_train'].dropna()
        y_train = prepared_data['y_train'].loc[X_train.index]
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test'].dropna()
            y_test = prepared_data['y_test'].loc[X_test.index]
        else:
            X_test = None
            y_test = None

        if result_key is None:
            result_key = y_train.columns[0]
            self.stats['result_key'] = result_key

        if isinstance(y_train, pd.DataFrame) and result_key in y_train.columns:
            y_train = prepared_data['y_train'][result_key]
            if y_test is not None:
                y_test = prepared_data['y_test'][result_key]
        elif not isinstance(y_train, (pd.Series, list, np.ndarray)):
            raise ValueError(
                'y_train and y_test must be a DataFrame with '
                'relevant column specified via result_key or '
                '1-D Array-like'
            )

        fit_data = {'X_train': X_train, 'y_train': y_train}
        if X_test is not None:
            fit_data['X_test'] = X_test
            fit_data['y_test'] = y_test

        return fit_data

    def train_model(self, input_data: dict):
        """
        This function can be used to build and train XGBRegression model.
        It also performs gridsearch which helps us to get optimal model
        parameters based on Mean Absolute Error.

        prepared_data requires keys: X_train, y_train, X_test, y_test
        """
        prepared_data = self.prepare_data(input_data)
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test']
            y_test = prepared_data['y_test']
        else:
            X_test = None
            y_test = None

        result_key = self.stats['result_key']
        max_features = self.stats['max_features']
        logger.info(f'Fitting model {self.name} for {result_key}')

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
        self.stats['input_features'] = features
        return model

    def evaluate_model(self, input_data, trained_model):
        """Calculate metrics"""
        fit_data = self.prepare_data(input_data)
        return evaluate_regression_base_model(
            fit_data,
            trained_model,
            features=trained_model.stats['selected_features'],
        )

    def train(self, data: Dict[str, Any] = None) -> Model:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        
        ml_model = self.train_model(data)
        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model
    

class XGBRegressionModeler:
    model_class = XGBRegressionModel

    def __init__(
        self,
        result_key: str = 'result',
        max_features: int = 50,
        eta: float = 0.001,
        n_estimators: int = 5,
        max_depth: int = 3,
        debug: bool = False,
    ) -> None:
        super().__init__()
        self.stats = {
            'result_key': result_key,
            'max_features': int(max_features),
            'eta': eta,
            'n_estimators': int(n_estimators),
            'max_depth': int(max_depth),
            'debug': debug,
        }

    def __get_model_build_params(self, model: XGBRegressionModel) -> dict:
        return {
            'max_depth': model.max_depth,
            'max_leaves': model.max_leaves,
            'max_bin': model.max_bin,
            'grow_policy': model.grow_policy,
            'learning_rate': model.learning_rate,
            'n_estimators': model.n_estimators,
            'verbosity': model.verbosity,
            'booster': model.booster,
            'tree_method': model.tree_method,
            'n_jobs': model.n_jobs,
            'gamma': model.gamma,
            'min_child_weight': model.min_child_weight,
            'max_delta_step': model.max_delta_step,
            'subsample': model.subsample,
            'sampling_method': model.sampling_method,
            'colsample_bytree': model.colsample_bytree,
            'colsample_bylevel': model.colsample_bylevel,
            'colsample_bynode': model.colsample_bynode,
            'reg_alpha': model.reg_alpha,
            'reg_lambda': model.reg_lambda,
            'scale_pos_weight': model.scale_pos_weight,
            'base_score': model.base_score,
            'random_state': model.random_state,
            'missing': model.missing,
            'num_parallel_tree': model.num_parallel_tree,
            'monotone_constraints': model.monotone_constraints,
            'interaction_constraints': model.interaction_constraints,
            'importance_type': model.importance_type,
            'gpu_id': model.gpu_id,
            'validate_parameters': model.validate_parameters,
            'predictor': model.predictor,
            'enable_categorical': model.enable_categorical,
            'feature_types': model.feature_types,
            'max_cat_to_onehot': model.max_cat_to_onehot,
            'max_cat_threshold': model.max_cat_threshold,
            'eval_metric': model.eval_metric,
            'early_stopping_rounds': model.early_stopping_rounds
        }

    def train_base_model(self, input_data: dict) -> XGBRegressor:
        """
        This function can be used to build and train XGBRegression model.
        It also performs gridsearch which helps us to get optimal model
        parameters based on Mean Absolute Error.

        prepared_data requires keys: X_train, y_train, X_test, y_test
        """
        prepared_data = self.prepare_data(input_data)
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test']
            y_test = prepared_data['y_test']
        else:
            X_test = None
            y_test = None

        result_key = self.stats['result_key']
        max_features = self.stats['max_features']
        logger.info(f'Fitting model {self.model_class.name} for {result_key}')

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

        max_depth = self.stats['max_depth']
        eta = self.stats['eta']
        n_estimators = self.stats['n_estimators']
        # if X_test is not None:
        #     fit_data['X_test'] = X_test[features]
        #     fit_data['y_test'] = y_test
        #     logger.info(
        #         'Found test data, grid searching to ' 'optimize hyperparameters.'
        #     )
        #     hyperparams = xgb_grid_search(
        #         fit_data,
        #         debug=self.stats['debug'],
        #         max_depth=max_depth,
        #         n_estimators=n_estimators,
        #         eta=eta,
        #     )
        #     max_depth, n_estimators, eta = hyperparams
        #     logger.info(
        #         f'Best hyperparmeters found:\n'
        #         f'n_estimators: {n_estimators}\n'
        #         f'max_depth: {max_depth}\n'
        #         f'eta: {eta}\n'
        #         f'Replacing passed hyperparameters.'
        #     )
        #     self.stats.update(
        #         {'max_depth': max_depth, 'n_estimators': n_estimators, 'eta': eta}
        #     )

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
        self.stats['input_features'] = features
        self.stats['build_params'] = self.__get_model_build_params(model)
        return model

    def prepare_data(self, prepared_data: dict):
        result_key = self.stats['result_key']

        # NaN/Inf should be handled in preprocessing but just in case
        X_train = prepared_data['X_train'].dropna()
        y_train = prepared_data['y_train'].loc[X_train.index]
        if 'X_test' in prepared_data:
            X_test = prepared_data['X_test'].dropna()
            y_test = prepared_data['y_test'].loc[X_test.index]
        else:
            X_test = None
            y_test = None

        if result_key is None:
            result_key = y_train.columns[0]
            self.stats['result_key'] = result_key

        if isinstance(y_train, pd.DataFrame) and result_key in y_train.columns:
            y_train = prepared_data['y_train'][result_key]
            if y_test is not None:
                y_test = prepared_data['y_test'][result_key]
        elif not isinstance(y_train, (pd.Series, list, np.ndarray)):
            raise ValueError(
                'y_train and y_test must be a DataFrame with '
                'relevant column specified via result_key or '
                '1-D Array-like'
            )

        fit_data = {'X_train': X_train, 'y_train': y_train}
        if X_test is not None:
            fit_data['X_test'] = X_test
            fit_data['y_test'] = y_test

        return fit_data

    def evaluate_model(self, input_data, trained_model):
        """Calculate metrics"""
        fit_data = self.prepare_data(input_data)
        return evaluate_regression_base_model(
            fit_data,
            trained_model.base_model,
            features=trained_model.stats['selected_features'],
        )

    def train_model(self, data: Dict[str, Any] = None):
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if self.model_class is None:
            raise ValueError('Model class not provided')

        if not data:
            data = self.load_data()
        
        base_model = self.train_base_model(data)

        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model

    def build_model(self, data: Dict[str, Any] = None):
        return self.train_model(data)
