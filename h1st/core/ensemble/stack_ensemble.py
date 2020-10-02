import numpy as np
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import RobustScaler
from typing import Dict, List, Any

from h1st.core.model import Model
from h1st.core.exception import ModelException
from h1st.core.ensemble import Ensemble


class StackEnsemble(Ensemble):
    """
    Base StackEnsemble class to implement StackEnsemble classifiers or regressors.
    """
    def __init__(self,
                 ensembler: MultiOutputClassifier,
                 sub_models: List[Model],
                 submodel_input_key: str,
                 submodel_output_key: str):
        super().__init__(ensembler, sub_models)
        self._submodel_input_key = submodel_input_key
        self._submodel_output_key = submodel_output_key

    def _preprocess(self, X: Any) -> Any:
        """
        Predicts all sub models then merge input raw data with predictions for ensembler's training or prediction
        :param X: raw input data
        """

        # Feed input_data to each sub-model and get predictions
        predictions = [
            m.predict({self._submodel_input_key: X})[self._submodel_output_key]
            for m in self._sub_models
        ]

        # Combine raw_data and predictions
        return np.hstack([X] + predictions)

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

        self.model.fit(X_train, y_train)

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
        return {'predictions': self.model.predict(X)}
