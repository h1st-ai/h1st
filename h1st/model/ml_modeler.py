from typing import Any, Dict
from h1st.model.modeler import Modeler
from h1st.model.ml_model import MLModel


class MLModeler(Modeler):
    """
    Base class for H1st ML Modeler.
    """
    
    def train(self, prepared_data: dict):
        """
        Implement logic of training model

        :param prepared_data: prepared data from ``prep`` method
        """
    
    def build(self) -> MLModel:
        """
        Implement logic to create the corresponding MLModel object.
        """
        data = self.load_data()
        base_model = self.train(data)
        if self.model_class is None:
            raise ValueError('Model class not provided')

        ml_model = self.model_class()
        ml_model.base_model = base_model
        
        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate(data, ml_model)
        return ml_model
