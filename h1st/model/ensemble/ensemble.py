from typing import Any, List
from h1st.model.ml_model import MLModel

from h1st.model.predictive_model import PredictiveModel

class Ensemble(PredictiveModel):
    """
    Base ensemble class.
    """
    pass

class MLEnsemble(Ensemble, MLModel):
    """
    Base machine learning ensemble class.
    """
    def __init__(self, ensembler, sub_models: List[PredictiveModel]):
        """
        :param ensembler: ensembler model, currently it is sklearn's MultiOutputClassifier
            when framework supports StackEnsembleRegressor,
            ensembler could be either MultiOutputClassifier or another specific base model
        :param sub_models: list of h1st.Model participating in the stack ensemble
        """
        self.base_model = ensembler
        self._sub_models = sub_models

    @property
    def base_model(self) -> Any:
        return getattr(self, "__base_model", None)

    @base_model.setter
    def base_model(self, value):
        setattr(self, "__base_model", value)
