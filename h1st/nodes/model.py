import abc
from typing import Any, Dict

from h1st.core.node import Node


class Model(Node):
    """
    Base class for H1st Model.
    To create your own model, inherit `Model` class and implement `process` accordingly.
    Please refer to Tutorial for more details how to create a model.
    The framework allows you to persist and load model to the model repository.
    To persist the model, you can call `persist()`, and then `load_params` to retrieve the model.
    See `persist()` and `load_params()` document for more detail.
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
           my_model_2.load_params('1st_version')
    """

    def execute(self, *previous_output: Any):
        self.predict(previous_output)

    @abc.abstractmethod
    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to process data
        :params data: data to process
        :returns: processed result as a dictionary
        """
        pass
