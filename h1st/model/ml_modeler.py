from email.mime import base
from typing import Any, Dict

from h1st.model.modelable import MLModelable
from .modeler import Modeler


class MLModeler(Modeler):
    """
    Base class for H1st ML Modelers. Has capabilities that are specific to MLModels.
    """

    def __init__(self, model_class, base_model: Any):
        self.__base_model = base_model
        super().__init__(model_class)

    def train_model(self, data: Dict) -> MLModelable:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if not data:
            data = self.load_data()
        
        ml_model = self.model_class(self.__base_model)
        ml_model.train_base_model(data)

        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model
    
    def build_model(self, data: Dict = None) -> MLModelable:
        return self.train_model(data)