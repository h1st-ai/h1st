from typing import Dict, List, Any

import numpy as np
from sklearn.preprocessing import RobustScaler
from h1st.model.ensemble.stack_ensemble import StackEnsemble
from h1st.model.ml_modeler import MLModeler
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ensemble.ensemble_modeler import EnsembleModeler
from h1st.model.model import Model


class StackEnsembleModeler(EnsembleModeler):
    """
    Base StackEnsemble class to implement StackEnsemble classifiers or regressors.
    """

    def __init__(self, ensembler_modeler, sub_models: List[PredictiveModel], **kwargs):
        """
        :param **kwargs: StackEnsemble use h1st models as submodels and the predict function of
        h1st model receives a dictionary and returns a dictionary. users can set the key of these
        dictionaries with the following keyword arguments.

            **submodel_predict_input_key (str): the default value of submodel_input_key is 'X' \n
            **submodel_predict_output_key (str): the default value of submodel_output_key is 'predictions'
        """
        self.ensembler_modeler = ensembler_modeler
        self._sub_models = sub_models
        self._submodel_predict_input_key = kwargs.get('submodel_predict_input_key', 'X')
        self._submodel_predict_output_key = kwargs.get('submodel_predict_output_key', 'predictions')
        self.model_class = StackEnsemble
        

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
        if data is None:
            data = self.load_data()

        if data is not None:
            X_train, y_train = (data['X_train'], data['y_train'])
            X_train = self.model_class.preprocess(self._sub_models,
                                                self._submodel_predict_input_key,
                                                self._submodel_predict_output_key,
                                                X_train
                                                )

            X_test, y_test = (data['X_test'], data['y_test'])
            X_test = self.model_class.preprocess(self._sub_models,
                                                self._submodel_predict_input_key,
                                                self._submodel_predict_output_key,
                                                X_test
                                                )

            ensembler = self.ensembler_modeler.build_model({'X_train': X_train, 'y_train': y_train,
                                                            'X_test': X_test, 'y_test': y_test,
                                                            })
        else:
            ensembler = self.ensembler_modeler.build_model()
        ensemble = self.model_class(ensembler=ensembler,
                                    sub_models=self._sub_models,
                                    submodel_predict_input_key=self._submodel_predict_input_key,
                                    submodel_predict_output_key=self._submodel_predict_output_key)
        return ensemble
