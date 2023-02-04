from typing import Any, Dict

from h1st.h1flow.h1step_containable import NodeContainable
from h1st.trust.trustable import Trustable

# TODO: Fix this before getting to use, expect to save locally, ideally use native save/ load way
# from h1st.model.repository.model_repository import ModelRepository

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

    ## TODO: Need a better naming and the definition of the property
    @property
    def model_class(self) -> Any:
        return getattr(self, "__model_class", None)

    @model_class.setter
    def model_class(self, value):
        setattr(self, "__model_class", value)

    @property
    def stats(self):
        return getattr(self, "__stats__", None)

    @stats.setter
    def stats(self, value) -> Dict:
        setattr(self, "__stats__", value)

    @property
    def metrics(self):
        if not hasattr(self, "__metrics__"):
            setattr(self, "__metrics__", {})
        return getattr(self, "__metrics__")

    @metrics.setter
    def metrics(self, value) -> Dict:
        setattr(self, "__metrics__", value)

    # def persist(self, version=None) -> str:
    #     """
    #     Persist this model's properties to the ModelRepository. Currently, only `stats`, `metrics`, `model` properties are supported.

    #     `model` property could be single model, list or dict of models
    #     Currently, only sklearn and tensorflow-keras are supported.

    #     :param version: model version, leave blank for autogeneration
    #     :returns: model version
    #     """
    #     repo = ModelRepository.get_model_repo(self)
    #     return repo.persist(model=self, version=version)

    # def load(self, version: str = None) -> Any:
    #     """
    #     Load parameters from the specified `version` from the ModelRepository.
    #     Leave version blank to load latest version.
    #     """
    #     repo = ModelRepository.get_model_repo(self)
    #     repo.load(model=self, version=version)

        return self

    def explore_data(self, data: Dict) -> None:
        """
        Implement logic to explore data from loaded data
        :param loaded_data: the data loaded using `load_data`.
        """
        pass

    def preprocess(self, input_data: Dict) -> Dict:
        """
        Implement logic to process data

        :params input_data: data to process
        :returns: processing result as a dictionary
        """
        # not raise NotImplementedError so the initial model created by integrator will just work
        return input_data

    def train(self, data: Dict[str, Any] = None) -> None:
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if self.model_class is None:
            raise ValueError('Model class not provided')

        if not data:
            data = self.load_data()
        
        base_model = self.train_base_model(data)

        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
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

        return None

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data is input data for prediction
        :returns: a dictionary with key `predictions` containing the predictions
        """
        return {"predictions": None}