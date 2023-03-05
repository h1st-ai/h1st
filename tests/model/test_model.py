import tempfile

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.model import Model
from h1st.model.repository.model_repository import ModelSerDe
from h1st.model.knowledge_model import RuleBasedModel


class MySkLearnEstimator(BaseEstimator, ClassifierMixin):
    def __init__(self):
        self.model = LogisticRegression()

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)


class TestModelSerDe:
    def assert_models(self, modeler_class, model_class, model_type, model_path, collection='none'):
        """
        Assert only 1st item in the list of models or the Iris key for dict
        """
        my_modeler = modeler_class()
        data = my_modeler.load_data()
        X, y = data['X'], data['y']

        my_modeler.model_class = model_class

        model = my_modeler.build_model()
        print(model.base_model)
        model_2 = model_class()
        model_serde = ModelSerDe()
        with tempfile.TemporaryDirectory() as path:
            # print(path)
            model_serde.serialize(model, path)

            # print(os.listdir(path))

            import yaml
            with open('%s/METAINFO.yaml' % path, 'r') as file:
                meta_info = yaml.load(file, Loader=yaml.Loader)
                assert type(meta_info) == dict
                if collection == 'list':
                    assert meta_info['models'][0]['model_path'] == model_path
                    assert meta_info['models'][0]['model_type'] == model_type
                elif collection == 'dict':
                    assert 'Iris' in meta_info['models'].keys()
                    assert meta_info['models']['Iris']['model_path'] == model_path
                    assert meta_info['models']['Iris']['model_type'] == model_type
            
            if model_type == 'sklearn':
                import joblib
                assert model_type == model_serde._get_model_type(joblib.load('%s/%s' % (path, model_path)))

            model_serde.deserialize(model_2, path)
            
            if collection == 'list':
                assert model_type == model_serde._get_model_type(model_2.base_model[0])
                assert model_2.base_model[0].predict(X).shape[0] == y.shape[0]
            elif collection == 'dict':
                assert model_type == model_serde._get_model_type(model_2.base_model['Iris'])
                assert model_2.base_model['Iris'].predict(X).shape[0] == y.shape[0]
            else:
                assert model_type == model_serde._get_model_type(model_2.base_model)
                assert model_2.base_model.predict(X).shape[0] == y.shape[0]

    def test_serialize_sklearn_model(self):
        class MyModeler(MLModeler):
            def load_data(self) -> dict:
                data = load_iris()
                return {'X': data.data, 'y': data.target}

            def train_base_model(self, prepared_data):
                model = LogisticRegression(random_state=0)
                X, y = prepared_data['X'], prepared_data['y']
                model.fit(X, y)
                return model

        class MyModel(MLModel):
            pass

        self.assert_models(MyModeler, MyModel, 'sklearn', 'model.joblib')

    def test_serialize_custom_sklearn_model(self):

        class MyModeler(MLModeler):
            def load_data(self) -> dict:
                data = load_iris()
                return {'X': data.data, 'y': data.target}

            def train_base_model(self, prepared_data):
                model = MySkLearnEstimator()
                X, y = prepared_data['X'], prepared_data['y']
                model.fit(X, y)
                return model

        class MyModel(MLModel):
            pass

        self.assert_models(MyModeler, MyModel, 'sklearn', 'model.joblib')

    def test_serialize_list_sklearn_model(self):
        class MyModeler(MLModeler):
            def load_data(self) -> dict:
                data = load_iris()
                return {'X': data.data, 'y': data.target}

            def train_base_model(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                return [LogisticRegression(random_state=0).fit(X, y), LogisticRegression(random_state=0).fit(X, y)]
        
        class MyModel(MLModel):
            pass

        self.assert_models(MyModeler, MyModel, 'sklearn', 'model_0.joblib', 'list')

    def test_serialize_dict_sklearn_model(self):
        class MyModeler(MLModeler):
            def load_data(self) -> dict:
                data = load_iris()
                return {'X': data.data, 'y': data.target}

            def train_base_model(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                return {'Iris': LogisticRegression(random_state=0).fit(X, y)}
        
        class MyModel(MLModel):
            pass

        self.assert_models(MyModeler, MyModel, 'sklearn', 'model_Iris.joblib', 'dict')

class TestModelStatsSerDe:
    def test_serialize_dict(self):
        class MyModeler(MLModeler):
            def __init__(self):
                super().__init__()
            
            def train_base_model(self, prepared_data):
                self.stats = {'CarSpeed': {'min': 0.01}}
                return None

        class MyModel(MLModel):
            pass

        my_modeler = MyModeler()
        my_modeler.model_class = MyModel
        model = my_modeler.build_model()

        model_2 = MyModel()

        model_serde = ModelSerDe()
        with tempfile.TemporaryDirectory() as path:
            # print(path)
            model_serde.serialize(model, path)

            # print(os.listdir(path))

            import yaml
            with open('%s/METAINFO.yaml' % path, 'r') as file:
                meta_info = yaml.load(file, Loader=yaml.Loader)
                print(meta_info)
                assert type(meta_info) == dict
                assert meta_info['stats'] == 'stats.joblib'

                import joblib
                assert 'CarSpeed' in joblib.load('%s/%s' % (path, 'stats.joblib')).keys()

                model_serde.deserialize(model_2, path)
                assert 'CarSpeed' in model_2.stats


class TestRuleModel:
    def test_ruled_based_model(self):
        class MyRule(RuleBasedModel):
            def predict(self, input_data):
                return {"result": sum(input_data['X'])}

        model = MyRule()
        assert {'result': 42} == model.predict({'X': [1, 1, 10, 10, 20]})
