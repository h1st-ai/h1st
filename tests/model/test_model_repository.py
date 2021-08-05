import tempfile
from unittest import TestCase

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from h1st.model.ml_model import MLModel
from h1st.model.repository import ModelRepository
from h1st.model.repository.storage import LocalStorage


class ModelRepositoryTestCase(TestCase):
    def test_serialize_sklearn_model(self):
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
                self.base_model = LogisticRegression(random_state=0)
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                self.base_model.fit(X, y)


        X, y = load_iris(return_X_y=True)
        prepared_data = {'X': X, 'y': y}

        model = MyModel()
        model.train(prepared_data)
        with tempfile.TemporaryDirectory() as path:
            mm = ModelRepository(storage=LocalStorage(storage_path=path))
            version = mm.persist(model=model)

            model_2 = MyModel()
            mm.load(model=model_2, version=version)

            assert 'sklearn' in str(type(model_2.base_model))

