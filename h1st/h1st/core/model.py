from typing import Any, List, NoReturn, Union
from ..schema import SchemaValidator
from ..model_repository import ModelRepository
from .node_containable import NodeContainable


class Model(NodeContainable):
    """
    Base class for H1ST Model.

    To create your own model, inherit `Model` class and implement `prepare_data`, `train` and
    `predict` accordingly. Please refer to Tutorial for more details how to create a model.

    The framework allows you to persist and load model to the model repository.
    To persist the model, you can call `persist()`, and then `load` to retrieve the model.
    See `persist()` and `load()` document for more detail.

        .. code-block:: python
           :caption: Model Persistence and Loading Example

           import h1st as h1
           from sklearn.datasets import load_iris
           from sklearn.linear_model import LogisticRegression

           class MyModel(h1.Model):
               def __init__(self):
                   super().__init__()
                   self.model = LogisticRegression(random_state=0)

               def train(self, prepared_data):
                   X, y = prepared_data['X'], prepared_data['y']
                   self.model.fit(X, y)

           my_model = MyModel()
           X, y = load_iris(return_X_y=True)
           prepared_data = {'X': X, 'y': y}
           my_model.train(prepared_data)
           # Persist the model to repo
           my_model.persist('1st_version')

           # Load the model from the repo
           my_model_2 = MyModel()
           my_model_2.load('1st_version')
    """

    def load_data(self) -> Any:
        """
        Implement logic of load data from data source

        :returns: loaded data
        """
        raise NotImplementedError()

    def prep_data(self, data: Any) -> Any:
        """
        Implement logic to prepare data from loaded data

        :param data: loaded data from ``load_data`` method
        :returns: prepared data
        """
        raise NotImplementedError()

    def explore(self) -> Any:
        """
        Implement logic to explore data from loaded data
        """
        raise NotImplementedError()

    def train(self, prepared_data: dict):
        """
        Implement logic of training model

        :param prepared_data: prepared data from ``prep_data`` method
        """
        # not raise NotImplementedError so the initial model created by integrator will just work
        pass

    def persist(self, version=None):
        """
        Persist this model's properties to the ModelRepository. Currently, only `stats`, `metrics`, `model` properties are supported.

        `model` property could be single model, list or dict of models
        Currently, only sklearn and tensorflow-keras are supported.

        :param version: model version, leave blank for autogeneration
        :returns: model version
        """
        mm = ModelRepository.get_model_repo(self)
        return mm.persist(model=self, version=version)

    def load(self, version: str = None):
        """
        Load the specified `version` from the ModelRepository. Leave version blank to load latest version.
        """
        mm = ModelRepository.get_model_repo(self)
        mm.load(model=self, version=version)

        return self

    def evaluate(self, data: dict):
        """
        Implement logic to evaluate the model using the loaded data

        :param data: loaded data
        """
        raise NotImplementedError()

    def predict(self, data: dict) -> dict:
        """
        Implement logic to generate prediction from data

        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        # not raise NotImplementedError so the initial model created by integrator will just work 
        return {}

    def test_output(self, input_data: Any = None, schema=None):
        """
        Validate the models' prediction with a schema.::
        :param input_data: input data for prediction, it can be anything.
        :param schema: target schema
        :return: validation result
        """
        prediction = self.predict(input_data)
        return SchemaValidator().validate(prediction, schema)

    def describe(self):
        """
        Implement logic to describe about your model
        """
        pass

    def explain(self, prediction: dict):
        """
        Implement logic to explain about a given prediction
        """
        pass
