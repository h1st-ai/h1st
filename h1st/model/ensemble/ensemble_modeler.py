from typing import List
from h1st.model.predictive_model import PredictiveModel
from h1st.model.modeler import Modeler
from h1st.model.ml_modeler import MLModeler

class EnsembleModeler(Modeler):
    pass

class MLEnsembleModeler(MLModeler):
    def __init__(self, ensembler, sub_models: List[PredictiveModel]):
        """
        :param ensembler: ensembler model, currently it is sklearn's MultiOutputClassifier
            when framework supports StackEnsembleRegressor,
            ensembler could be either MultiOutputClassifier or another specific base model
        :param sub_models: list of h1st.Model participating in the stack ensemble
        """
        self.stats = {}
        self.base_model = ensembler
        self._sub_models = sub_models