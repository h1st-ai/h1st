from typing import Dict, List, Any
import numpy as np
from h1st.model.ensemble.ensemble import Ensemble
from h1st.model.predictive_model import PredictiveModel


class StackEnsemble(Ensemble):
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
        self.ensembler = ensembler
        self._sub_models = sub_models
        self._submodel_predict_input_key = kwargs.get('submodel_predict_input_key', 'X')
        self._submodel_predict_output_key = kwargs.get('submodel_predict_output_key', 'predictions')

    @classmethod
    def preprocess(cls, sub_models: List[PredictiveModel],
                        submodel_predict_input_key: str,
                        submodel_predict_output_key: str,
                        X: Any) -> Any:
        """
        Predicts all sub models then merge input raw data with predictions for ensembler's training or prediction
        :param X: raw input data
        """
        if isinstance(X, list):
            predictions = [np.hstack((x, StackEnsemble.get_submodels_prediction(sub_models,
                                                                  submodel_predict_input_key,
                                                                  submodel_predict_output_key, x)))
                                                                for x in X]
            return np.vstack(predictions)
        else:
            return np.hstack((X, StackEnsemble.get_submodels_prediction(sub_models,
                                                        submodel_predict_input_key,
                                                        submodel_predict_output_key,
                                                        X
                                                        )))

    @classmethod
    def get_submodels_prediction(cls, sub_models: List[PredictiveModel], submodel_predict_input_key: str, submodel_predict_output_key: str, X: Any) -> Any:
        preds = []
        for m in sub_models:
            pred = m.predict({submodel_predict_input_key: X})
            output_key = pred.get(submodel_predict_output_key)
            if output_key is not None:
                preds.append(output_key.reshape(-1,1))
        return np.hstack(preds)

    def predict(self, data: Dict) -> Dict:
        """
        Returns predictions of ensembler model for input raw data combining with predictions from sub models

        This method will raise ModelException if ensembler model has not been trained.

        :param data: must be a dictionary {'X': ...}, with X is raw data (numeric only)
        :return:
            output will be a dictionary {'predictions': ....}
        """
        X = StackEnsemble.preprocess(self._sub_models,
                                     self._submodel_predict_input_key,
                                     self._submodel_predict_output_key,
                                     data['X']
                                    )
        return {'predictions': self.ensembler.predict({'X': X})['predictions']}

    def persist(self, version=None):
        version = self.ensembler.persist(version)
        version = super().persist(version)
        return version

    def load_params(self, version: str = None) -> None:
        self.ensembler.load_params(version)
        super().load_params(self.ensembler.version)
