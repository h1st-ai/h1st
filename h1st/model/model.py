from typing import Any, Dict

from h1st.h1flow.h1step_containable import NodeContainable
from h1st.trust.trustable import Trustable

# TODO: Fix this before getting to use, expect to save locally, ideally use native save/ load way
from h1st.model.repository.model_repository import ModelRepository

class Model(NodeContainable, Trustable):
    """
    Base class for H1st Model.

    To create your own model, inherit `Model` class and implement `process` accordingly.
    Please refer to Tutorial for more details how to create a model.

    The framework allows you to persist and load model to the model repository.
    To persist the model, you can call `persist()`, and then `load` to retrieve the model.
    See `persist()` and `load()` document for more detail.

        .. code-block:: python
           :caption: Model Persistence and Loading Example

           import h1st

           class MyModeler(h1st.model.Modeler):
               def build_model(self):
                   ...

           class MyModel(h1st.model.Model):



           my_modeler = MyModeler()
           my_modeler.model_class = MyModel

           my_model = my_modeler.build_model()

           # Persist the model to repo
           my_model.persist('1st_version')

           # Load the model from the repo
           my_model_2 = MyModel()
           my_model_2.load('1st_version')
    """
    def __init__(self):
        super().__init__()
        self.stats = {}
        self.metrics = {}
        self.base_model = None

    def persist(self, path: str, version: str = None) -> str:
        """
        Persist this model's properties to the ModelRepository. Currently, only `stats`, `metrics`, `model` properties are supported.

        `model` property could be single model, list or dict of models
        Currently, only sklearn and tensorflow-keras are supported.

        :param version: model version, leave blank for autogeneration
        :returns: model version
        """
        repo = ModelRepository(storage=path)
        return repo.persist(model=self, version=version)

    def load(self, path: str, version: str = None) -> Any:
        """
        Load parameters from the specified `version` from the ModelRepository.
        Leave version blank to load latest version.
        """
        repo = ModelRepository(storage=path)
        repo.load(model=self, version=version)

        return self

    def train(self, data: Dict[str, Any] = None) -> None:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if self.model_class is None:
            raise ValueError('Model class not provided')

        if not data:
            data = self.load_data()
        
        base_model = self.train_base_model(data)
        self.base_model = base_model

        ml_model = self.model_class()
        ml_model.base_model = base_model

        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        
        ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model

    def evaluate(self, data: Dict, model: Dict) -> Dict:
        """
        Implement logic to evaluate the model using the prepared_data
        This function will calculate model metrics and store it into self.metrics

        :param prepared_data: the prepared data
        :param model: the corresponding h1st `Model` to evaluate against.
        """
        if type(model) != self.model_class:
            raise ValueError(
                "The provided model is not a %s" % self.model_class.__name__
            )

        return {'data': data}

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data is input data for prediction
        :returns: a dictionary with key `predictions` containing the predictions
        """
        return {"predictions": input_data}