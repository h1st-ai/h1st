from typing import Any, Dict
from enum import Enum

from h1st.model.modelable import MLModelable
from .modeler import Modeler


class BaseModelType(Enum):
    SCIKITLEARN = 1
    PYTORCH = 2
    TENSORFLOW = 3
    UNKNOWN = 99

    
class MLModeler(Modeler):
    """
    Base class for H1st ML Modelers. Has capabilities that are specific to MLModels.
    """

    def __init__(self, model_class, base_model: Any = None):
        self.__base_model = base_model
        super().__init__(model_class)

    def build_model(self, data: Dict = None) -> MLModelable:
        return self.train_model(data)

    def train_model(self, data: Dict) -> MLModelable:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if not data:
            data = self.load_data()
        
        ml_model = self.model_class(self.__base_model)
        self.train_base_model(ml_model, data)
#        ml_model.train_base_model(data)

#        # Pass stats to the model
#        if self.stats is not None:
#            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model
    
    def train_base_model(self, ml_model: MLModelable, data: Dict[str, Any]) -> Any:
        base_model_type = self.get_base_model_type(ml_model)

        if base_model_type == BaseModelType.SCIKITLEARN:
            ml_model.base_model.fit(data['features'], data['label'])

        elif base_model_type == BaseModelType.PYTORCH:
            pass

        elif base_model_type == BaseModelType.TENSORFLOW:
            pass

        else:
            pass

        return ml_model.base_model
    
    @classmethod
    def get_base_model_type(cls, ml_model: MLModelable) -> BaseModelType:
        module_name = ml_model.base_model.__module__.split(".")[0]

        if module_name == "sklearn":
            return BaseModelType.SCIKITLEARN

        elif module_name == "pytorch":
            return BaseModelType.PYTORCH

        elif module_name == "tensorflow":
            return BaseModelType.TENSORFLOW

        else:
            return BaseModelType.UNKNOWN