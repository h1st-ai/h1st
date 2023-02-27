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
    
    def train_model(self, data: Dict[str, Any] = None):
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if self.model_class is None:
            raise ValueError('Model class not provided')

        if not data:
            data = self.load_data()
        
        base_model = self.train_base_model(data)

        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        # ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model

    def build_model(self, data: Dict[str, Any] = None):
        return self.train_model(data)


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
    
    def train_model(self, data: Dict[str, Any] = None):
        """
        Implement logic to create the corresponding MLModel, including both training and evaluation.
        """
        if self.model_class is None:
            raise ValueError('Model class not provided')

        if not data:
            data = self.load_data()
        
        base_model = self.train_base_model(data)

        ml_model = self.model_class()
        ml_model.base_model = base_model

        # Pass stats to the model
        if self.stats is not None:
            ml_model.stats = self.stats.copy()
        # Compute metrics and pass to the model
        # ml_model.metrics = self.evaluate_model(data, ml_model)
        return ml_model

    def build_model(self, data: Dict[str, Any] = None):
        return self.train_model(data)
