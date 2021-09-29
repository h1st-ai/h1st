import tempfile

import tensorflow as tf
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from h1st.model.ml_model import MLModel
from h1st.model.model import Model
from h1st.model.repository import ModelSerDe
from h1st.model.rule_based_model import RuleBasedModel


class MySkLearnEstimator(BaseEstimator, ClassifierMixin):
    def __init__(self):
        self.model = LogisticRegression()

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)


class TestModelSerDe:
    def assert_models(self, model_class, model_type, model_path, collection='none'):
        """
        Assert only 1st item in the list of models or the Iris key for dict
        """
        X, y = load_iris(return_X_y=True)
        prepared_data = {'X': X, 'y': y}

        model = model_class()
        model.train(prepared_data)
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
            elif model_type == 'tensorflow-keras':
                # Currently, we save/load weights => nothing do assert here 
                pass

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
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
                self.base_model = LogisticRegression(random_state=0)
            
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                self.base_model.fit(X, y)

        self.assert_models(MyModel, 'sklearn', 'model.joblib')

    def test_serialize_custom_sklearn_model(self):

        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
                self.base_model = MySkLearnEstimator()
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                self.base_model.fit(X, y)

        self.assert_models(MyModel, 'sklearn', 'model.joblib')

    def test_serialize_list_sklearn_model(self):
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
            
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                self.base_model = [LogisticRegression(random_state=0).fit(X, y), LogisticRegression(random_state=0).fit(X, y)]

        self.assert_models(MyModel, 'sklearn', 'model_0.joblib', 'list')

    def test_serialize_dict_sklearn_model(self):
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
            
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                self.base_model = {'Iris': LogisticRegression(random_state=0).fit(X, y)}

        self.assert_models(MyModel, 'sklearn', 'model_Iris.joblib', 'dict')

    def test_serialize_tensorflow_model(self):
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
                self.base_model = tf.keras.Sequential([
                                                tf.keras.layers.Dense(8, input_dim=4, activation='relu'),
                                                tf.keras.layers.Dense(1, activation='softmax')
                                                ])
            
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                
                self.base_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
                self.base_model.fit(X, y, verbose=2, batch_size=5, epochs=20)

        self.assert_models(MyModel, 'tensorflow-keras', 'model')

    def test_serialize_dict_tensorflow_model(self):
        class MyModel(MLModel):
            def __init__(self):
                super().__init__()
                model = tf.keras.Sequential([
                                                tf.keras.layers.Dense(8, input_dim=4, activation='relu'),
                                                tf.keras.layers.Dense(1, activation='softmax')
                                                ])
                
                self.base_model = {'Iris': model}
            
            def train(self, prepared_data):
                X, y = prepared_data['X'], prepared_data['y']
                
                self.base_model['Iris'].compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
                self.base_model['Iris'].fit(X, y, verbose=2, batch_size=5, epochs=20)

        self.assert_models(MyModel, 'tensorflow-keras', 'model_Iris', 'dict')


class TestModelStatsSerDe:
    def test_serialize_dict(self):
        class MyModel(Model):
            def __init__(self):
                super().__init__()
            
            def train(self, reload_data=False):
                self.stats = {'CarSpeed': {'min': 0.01}}

        model = MyModel()
        model.train()

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
