import tempfile
from unittest import TestCase

from typing import Any, Dict
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.repository.model_repository import ModelRepository
from h1st.model.repository.storage.local import LocalStorage


class ModelRepositoryTestCase(TestCase):
    def test_serialize_sklearn_model(self):
        class MyModeler(MLModeler):
            def load_data(self) -> dict:
                data = load_iris()
                return {'X': data.data, 'y': data.target}

            def train(self, prepared_data):
                model = LogisticRegression(random_state=0)
                X, y = prepared_data['X'], prepared_data['y']
                model.fit(X, y)
                return model

        class MyModel(MLModel):
            pass

        my_modeler = MyModeler()
        my_modeler.model_class = MyModel

        model = my_modeler.build_model()
        with tempfile.TemporaryDirectory() as path:
            mm = ModelRepository(storage=LocalStorage(storage_path=path))
            version = mm.persist(model=model)

            model_2 = MyModel()
            mm.load(model=model_2, version=version)

            assert 'sklearn' in str(type(model_2.base_model))

