from typing import Any, Dict
from .ml_model import MLModel
from .modeler import Modeler


class MLModeler(Modeler):
    """
    Base class for H1st ML Modelers. Has capabilities that are specific to MLModels.
    """
    
    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        """
        Implement logic of training the base model

        :param prepared_data: prepared data from ``load_data`` method
        """
    
    def build_model(self) -> MLModel:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation. 
        """
        data = self.load_data()
        base_model = self.train_base_model(data)
        if self.model_class is None:
            raise ValueError('Model class not provided')

        ml_model = self.model_class()
        ml_model.base_model = base_model
        
        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model
