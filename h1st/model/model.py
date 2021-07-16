from typing import Any, NoReturn
# from h1st.schema import SchemaValidator
from h1st.model.repository import ModelRepository
from h1st.h1flow.h1step_containable import NodeContainable
from h1st.trust.trustable import Trustable
# from h1st.schema.schema_validation_result import SchemaValidationResult


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

           import h1st.core as h1

           class MyModel(h1.Model):
               def train(self, prepared_data):
                   X, y = prepared_data['X'], prepared_data['y']
                   ...

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

    ## TODO: Need a better naming and the definition of the property
    @property
    def stats(self):
        return getattr(self, '__stats__', None)

    @stats.setter
    def stats(self, value) -> dict:
        setattr(self, '__stats__', value)

    @property
    def metrics(self):
        if not hasattr(self, '__metrics__'):
            setattr(self, '__metrics__', {})
        return getattr(self, '__metrics__')

    @metrics.setter
    def metrics(self, value) -> dict:
        setattr(self, '__metrics__', value)

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

    def evaluate(self, prepared_data: dict) -> NoReturn:
        """
        Implement logic to evaluate the model using the prepared_data
        This function will calculate model metrics and store it into self.metrics

        :param data: loaded data
        """

    def load_prep_train_eval(self) -> NoReturn:
        """
        Run a cycle of modeling process which calls the following function in order:
        load_data -> prep -> train -> evaluate
        """
        loaded_data = self.load_data()
        prepared_data = self.prep(loaded_data)
        self.train(prepared_data)
        self.evaluate(prepared_data)
        
    def predict(self, input_data: dict) -> dict:
        """
        Implement logic to generate prediction from data

        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        # not raise NotImplementedError so the initial model created by integrator will just work 
        return {"input_data" : input_data}

    # def validate_node_output(self, input_data: dict=None, schema=None) -> SchemaValidationResult:
    #     """
    #     From `NodeContainable`. Validates the models' prediction with a schema.::
    #     :param input_data: input data for prediction, it can be anything.
    #     :param schema: target schema
    #     :return: validation result
    #     """
    #     return super().validate_node_output(self.predict(input_data), schema)
