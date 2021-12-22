from typing import Any, Dict
from h1st.model.modeler import Modeler
from h1st.model.ml_model import MLModel


class MLModeler(Modeler):
    """
    Base class for H1st ML Modeler.
    """
    @property
    def model_class(self) -> Any:
        return getattr(self, "__model_class", None)

    @model_class.setter
    def model_class(self, value):
        setattr(self, "__model_class", value)
    
    def build(self) -> MLModel:
        """
        Implement logic to create the corresponding MLModel object.
        """
        data = self.load_data()
        training_data = self.generate_training_data(data)
        base_model = self.train(training_data)
        ml_model = self.model_class()
        ml_model.base_model = base_model
        
        # Pass stats to the model
        ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate(training_data, ml_model.base_model)
        return ml_model