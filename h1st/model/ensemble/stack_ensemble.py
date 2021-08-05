from typing import Dict, List, Any

import numpy as np
from sklearn.preprocessing import RobustScaler

from h1st.exceptions.exception import ModelException
from h1st.model.ensemble.ensemble import Ensemble
from h1st.model.model import Model


class StackEnsemble(Ensemble):
    """
    Base StackEnsemble class to implement StackEnsemble classifiers or regressors.
    """

    def __init__(self, ensembler, sub_models: List[Model], **kwargs):
        """
        :param **kwargs: StackEnsemble use h1st models as submodels and the predict function of
        h1st model receives a dictionary and returns a dictionary. users can set the key of these
        dictionaries with the following keyword arguments.

            **submodel_predict_input_key (str): the default value of submodel_input_key is 'X' \n
            **submodel_predict_output_key (str): the default value of submodel_output_key is 'predictions'
        """
        super().__init__(ensembler, sub_models)
        self._submodel_predict_input_key = kwargs.get('submodel_predict_input_key', 'X')
        self._submodel_predict_output_key = kwargs.get('submodel_predict_output_key', 'predictions')

    def _preprocess(self, X: Any) -> Any:
        """
        Predicts all sub models then merge input raw data with predictions for ensembler's training or prediction
        :param X: raw input data
        """
        if isinstance(X, list):
            predictions = [self._get_submodels_prediction(x) for x in X]
            return np.vstack(predictions)
        else:
            return self._get_submodels_prediction(X)

    def _get_submodels_prediction(self, X: Any) -> Any:
        preds = []
        for m in self._sub_models:
            pred = m.predict({self._submodel_predict_input_key: X})
            output_key = pred.get(self._submodel_predict_output_key)
            if output_key is not None:
                preds.append(output_key)
        return np.hstack(preds)

    def train(self, prepared_data: Dict):
        """
        Trains ensembler with input is merging raw data 'X_train' and predictions of sub models, with targets 'y_train'
        'X_train' is supposed to be numeric.
        :param prepared_data: output of prep() implemented in subclass of StackEnsemble, its structure must be this dictionary
            {
                'X_train': ...,
                'X_test': ...,
                'y_train': ...,
                'y_test': ...
            }
        """
        X_train, y_train = (prepared_data['X_train'], prepared_data['y_train'])
        X_train = self._preprocess(X_train)
        scaler = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        self.stats = scaler.fit(X_train)
        X_train = self.stats.transform(X_train)

        self.base_model.fit(X_train, y_train)

    def predict(self, data: Dict) -> Dict:
        """
        Returns predictions of ensembler model for input raw data combining with predictions from sub models

        This method will raise ModelException if ensembler model has not been trained.

        :param data: must be a dictionary {'X': ...}, with X is raw data (numeric only)
        :return:
            output will be a dictionary {'predictions': ....}
        """
        if not self.stats:
            raise ModelException('This model has not been trained')

        X = self._preprocess(data['X'])
        X = self.stats.transform(X)
        return {'predictions': self.base_model.predict(X)}
