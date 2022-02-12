from typing import Dict, List, Any

import numpy as np
from sklearn import ensemble
from sklearn.preprocessing import RobustScaler
from h1st.model.ensemble.stack_ensemble import StackEnsemble
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ensemble.ensemble_modeler import MLEnsembleModeler
from h1st.model.model import Model


class StackEnsembleModeler(MLEnsembleModeler):
    """
    Base StackEnsemble class to implement StackEnsemble classifiers or regressors.
    """

    def __init__(self, ensembler, sub_models: List[PredictiveModel], **kwargs):
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
        self.model_class = StackEnsemble

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        X_train, y_train = (prepared_data['X_train'], prepared_data['y_train'])
        X_train = self.model_class.preprocess(self._sub_models,
                                              self._submodel_predict_input_key,
                                              self._submodel_predict_output_key,
                                              X_train
                                              )
        scaler = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        self.stats['scaler'] = scaler.fit(X_train)
        X_train = self.stats['scaler'].transform(X_train)

        self.base_model.fit(X_train, y_train)
        return self.base_model
        

    def build_model(self, data: Dict[str, Any] = None) -> StackEnsemble:
        """
        Trains an ensembler with input is merging raw data 'X_train' and predictions of sub models, with targets 'y_train'
        'X_train' is supposed to be numeric.
        :param prepared_data: output of prep() implemented in subclass of StackEnsemble, its structure must be this dictionary
            {
                'X_train': ...,
                'X_test': ...,
                'y_train': ...,
                'y_test': ...
            }
        """
        if not data:
            data = self.load_data()

        ensembler = self.train_base_model(data)
        ensemble = self.model_class(ensembler=ensembler,
                                    sub_models=self._sub_models,
                                    submodel_predict_input_key=self._submodel_predict_input_key,
                                    submodel_predict_output_key=self._submodel_predict_output_key)
        # Pass stats to the model
        if self.stats is not None:
            ensemble.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ensemble.metrics = self.evaluate_model(data, ensemble)
        return ensemble
