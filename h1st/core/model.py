from typing import Any
from h1st.schema import SchemaValidator
from h1st.model_repository import ModelRepository
from h1st.core.node_containable import NodeContainable
from h1st.core.trust.trustable import Trustable
from h1st.schema.schema_validation_result import SchemaValidationResult


class Model(NodeContainable, Trustable):
    """
    Base class for H1st Model.

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

    def load_data(self) -> dict:
        """
        Implement logic of load data from data source

        :returns: loaded data
        """

    def prep(self, loaded_data: dict) -> dict:
        """
        Implement logic to prepare data from loaded data

        :param data: loaded data from ``load_data`` method
        :returns: prepared data
        """

    def explore(self, loaded_data: dict) -> None:
        """
        Implement logic to explore data from loaded data
        """

    def train(self, prepared_data: dict):
        """
        Implement logic of training model

        :param prepared_data: prepared data from ``prep`` method
        """

    def persist(self, version=None):
        """
        Persist this model's properties to the ModelRepository. Currently, only `stats`, `metrics`, `model` properties are supported.

        `model` property could be single model, list or dict of models
        Currently, only sklearn and tensorflow-keras are supported.

        :param version: model version, leave blank for autogeneration
        :returns: model version
        """
        repo = ModelRepository.get_model_repo(self)
        return repo.persist(model=self, version=version)

    def load(self, version: str = None) -> "Model":
        """
        Load parameters from the specified `version` from the ModelRepository.
        Leave version blank to load latest version.
        """
        repo = ModelRepository.get_model_repo(self)
        repo.load(model=self, version=version)

        return self

    def evaluate(self, data: dict) -> dict:
        """
        Implement logic to evaluate the model using the loaded data

        :param data: loaded data
        """

    def predict(self, input_data: dict) -> dict:
        """
        Implement logic to generate prediction from data

        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        # not raise NotImplementedError so the initial model created by integrator will just work 
        return {"input_data" : input_data}

    def validate_node_output(self, input_data: dict=None, schema=None) -> SchemaValidationResult:
        """
        From `NodeContainable`. Validates the models' prediction with a schema.::
        :param input_data: input data for prediction, it can be anything.
        :param schema: target schema
        :return: validation result
        """
        return super().validate_node_output(self.predict(input_data), schema)
