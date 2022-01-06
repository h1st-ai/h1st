from typing import Any

from .predictive_model import PredictiveModel


class MLModel(PredictiveModel):
    """
    Base class for H1st Model.

    To create your own Machine Learning model, inherit `MLModel` class and implement `prepare_data`, 
    `train` and `predict` accordingly. Please refer to Tutorial for more details how to create a model.

    The framework allows you to persist and load model to the model repository.
    To persist the model, you can call `persist()`, and then `load` to retrieve the model.
    See `persist()` and `load_params()` document for more detail.

        .. code-block:: python
           :caption: Model Persistence and Loading Example

           import h1st.core as h1
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
           my_model_2.load_params('1st_version')
    """

    @property
    def base_model(self) -> Any:
        return getattr(self, "__base_model", None)

    @base_model.setter
    def base_model(self, value):
        setattr(self, "__base_model", value)
