import itertools
import pandas as pd
import numpy as np

from typing import Tuple
from xgboost import XGBRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import (
    mean_absolute_percentage_error,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def extratree_rank_features(x: pd.DataFrame, y: pd.DataFrame) -> Tuple[list, list]:
    '''
    takes dataframe and series and ranks the dataframe columns by importance to
    an ExtraTreeRegressor

    returns ordered list of features and list of feature important values
    '''
    # Initializing ExtraTreeClassRegressor
    extra_tree_forest = ExtraTreesRegressor(criterion='absolute_error', random_state=42)
    extra_tree_forest.fit(x, y)

    # Getting feature with importance
    ranked_feature = pd.Series(extra_tree_forest.feature_importances_, index=x.columns)
    ranked_feature = ranked_feature.sort_values(ascending=False)
    return ranked_feature.index.tolist(), ranked_feature.tolist()


def evaluate_regression_base_model(
    prepared_data: dict, model: XGBRegressor, features: list = None
) -> dict:
    '''Predicting and evaluating the results'''
    # Predicting the results
    if features is None:
        features = prepared_data['X_train'].columns.tolist()

    X_train = prepared_data['X_train'][features].copy()
    y_train_pred = model.predict(X_train)
    y_train_true = prepared_data['y_train'].to_numpy()

    metrics: dict = {}
    metrics.update(get_metrics(y_train_true, y_train_pred, 'train'))
    if 'X_test' in prepared_data:
        X_test = prepared_data['X_test'][features].copy()
        y_test_pred = model.predict(X_test)
        y_test_true = prepared_data['y_test'].to_numpy()
        metrics.update(get_metrics(y_test_true, y_test_pred, 'test'))

    return metrics


def get_metrics(y_true: np.ndarray, y_pred: np.ndarray, data_name: str) -> dict:
    '''Evaluating for temperature model'''
    metrics = {}
    metrics[f'{data_name}_mape'] = round(
        mean_absolute_percentage_error(y_true, y_pred), 2
    )
    metrics[f'{data_name}_mae'] = round(mean_absolute_error(y_true, y_pred), 2)

    '''Additional Evaluations'''
    metrics[f'{data_name}_mse'] = round(mean_squared_error(y_true, y_pred), 2)
    metrics[f'{data_name}_rmse'] = round(
        mean_squared_error(y_true, y_pred, squared=False), 2
    )
    metrics[f'{data_name}_nrmse_minmax'] = round(
        (
            (mean_squared_error(y_true, y_pred, squared=False))
            / (y_true.max() - y_true.min())
        ),
        2,
    )
    metrics[f'{data_name}_nrmse_iq'] = round(
        (
            (mean_squared_error(y_true, y_pred, squared=False))
            / (np.quantile(y_true, 0.75) - np.quantile(y_true, 0.25))
        ),
        2,
    )
    metrics[f'{data_name}_nrmse_sd'] = round(
        ((mean_squared_error(y_true, y_pred, squared=False)) / (np.std(y_true))), 2
    )
    metrics[f'{data_name}_nrmse_mean'] = round(
        ((mean_squared_error(y_true, y_pred, squared=False)) / (np.mean(y_true))), 2
    )
    metrics[f'{data_name}_rsquared'] = round(r2_score(y_true, y_pred), 2)
    return metrics


def xgb_grid_search(
    prepared_data: dict,
    debug: bool = False,
    max_depth: int = None,
    n_estimators: int = None,
    eta: float = None,
) -> Tuple[int, int, float]:
    '''Grid Search : Trying diffferent parameter for model. Evaluating
    model predictions by mae and returning best parameter'''
    # Parameter tuning for max_depth,n_Estimators and ETA for XGBoost
    if max_depth is None and debug:
        max_depth = [2]
    elif max_depth is None:
        max_depth = [2, 3, 4, 5, 6, 8, 10]
    elif not isinstance(max_depth, list):
        max_depth = [max_depth]

    if n_estimators is None and debug:
        n_estimators = [5, 10]
    elif n_estimators is None:
        n_estimators = [5, 10, 20, 30, 40, 50, 70, 100]
    elif not isinstance(n_estimators, list):
        n_estimators = [n_estimators]

    if eta is None and debug:
        eta = [0.001]
    elif eta is None:
        eta = [0.001, 0.01, 0.1, 0.2, 0.3, 0.5, 0.05]
    elif not isinstance(eta, list):
        eta = [eta]

    params = [max_depth, n_estimators, eta]
    gridsearch_results = []
    gridsearch_columns = ['max_depth', 'n_estimator', 'lr']

    # Iterating over all parameter combinations
    for tup in itertools.product(*params):
        model = XGBRegressor(max_depth=tup[0], n_estimators=tup[1], eta=tup[2], seed=42)
        model.fit(prepared_data['X_train'], prepared_data['y_train'].values)

        metrics = evaluate_regression_base_model(prepared_data, model)
        gridsearch_results.append(list(tup) + (list(metrics.values())))

    gridsearch_columns.extend(list(metrics.keys()))
    gridsearch_df = pd.DataFrame(gridsearch_results, columns=gridsearch_columns)
    # Selecting best model based on test_mape
    gridsearch_df = gridsearch_df.sort_values('test_mape')
    best_max_depth, best_n_estimator, best_eta = tuple(
        gridsearch_df[['max_depth', 'n_estimator', 'lr']].iloc[0]
    )
    return (int(best_max_depth), int(best_n_estimator), best_eta)
