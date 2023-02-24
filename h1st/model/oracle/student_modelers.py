from typing import Any, Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from h1st.model.oracle.student_models import RandomForestModel, LogisticRegressionModel


class RandomForestModeler:
    '''
    Knowledge Generalization Modeler backed by a RandomForest algorithm.
    '''

    def __init__(self, model_class=None, result_key=None):
        self.stats = {}
        self.model_class = model_class if model_class is not None else RandomForestModel

    def _preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        X = self._preprocess(prepared_data['X_train'])
        y = prepared_data['y_train']
        model = RandomForestClassifier(max_depth=20, random_state=1)
        model.fit(X, y)
        self.stats['input_features'] = list(prepared_data['X_train'].columns)
        self.stats['output_labels'] = list(prepared_data['y_train'].columns)
        return model


class LogisticRegressionModeler:
    '''
    Knowledge Generalization Modeler backed by a Logistic Regression algorithm
    '''

    def __init__(self, model_class=None, result_key=None):
        self.stats = {}
        self.model_class = (
            model_class if model_class is not None else LogisticRegressionModel
        )

    def _preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        X = self._preprocess(prepared_data['X_train'])
        y = prepared_data['y_train']
        model = LogisticRegression()
        model.fit(X, y)
        self.stats['input_features'] = list(prepared_data['X_train'].columns)
        self.stats['output_labels'] = list(prepared_data['y_train'].columns)
        return model
