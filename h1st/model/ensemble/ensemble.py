from typing import List

from h1st.model.ml_model import MLModel
from h1st.model.model import Model


class Ensemble(MLModel):
    """
    Base Ensemble class to implement various ensemble classes in the future
    even though we currently only have StackEnsemble.
    """

    def __init__(self, ensembler, sub_models: List[Model]):
        """
        :param ensembler: ensembler model, currently it is sklearn's MultiOutputClassifier
            when framework supports StackEnsembleRegressor,
            ensembler could be either MultiOutputClassifier or another specific base model
        :param sub_models: list of h1st.Model participating in the stack ensemble
        """
        self.base_model = ensembler
        self._sub_models = sub_models
