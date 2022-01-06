from typing import Any

from h1st.h1flow.h1step_containable import NodeContainable

from .modelable import Modelable


class Modeler(NodeContainable):
    """
    Base class for H1st Modeler.

    To create your own modeller, inherit `Modeler` class and implement `load_data`, `explore`, `train`,
    `evaluate and `build` accordingly. Please refer to Tutorial for more details how to create a model.
    The framework allows you to persist and load model to the model repository.
    To persist the model, you can call `persist()`, and then `load` to retrieve the model.
    See `persist()` and `load()` document for more detail.

        .. code-block:: python
           :caption: Model Persistence and Loading Example

           import h1st

           class MyModeler(h1st.model.Modeler):
               def train(self, prepared_data):
                   X, y = prepared_data['X'], prepared_data['y']
                   ...
               def build(self):
                   ...

           class MyModel(h1st.model.Model):
               


           my_modeler = MyModeler()
           my_modeler.model_class = MyModel

           my_model = my_modeler.build_model()

           # Persist the model to repo
           my_model.persist('1st_version')

           # Load the model from the repo
           my_model_2 = MyModel()
           my_model_2.load_params('1st_version')
    """
    @property
    def model_class(self) -> Any:
        return getattr(self, "__model_class", None)

    @model_class.setter
    def model_class(self, value):
        setattr(self, "__model_class", value)

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

    def explore_data(self, loaded_data: dict) -> None:
        """
        Implement logic to explore data from loaded data
        """

    def evaluate_model(self, prepared_data: dict, model: Modelable) -> dict:
        """
        Implement logic to evaluate the model using the prepared_data
        This function will calculate model metrics and store it into self.metrics

        :param data: loaded data
        """
        if type(model) != self.model_class:
            raise ValueError('The provided model is not a %s' % self.model_class.__name__)
        
        return None
    
    def build_model(self) -> Modelable:
        """
        Implement logic to create the corresponding Model object
        """
