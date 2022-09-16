from re import X
from typing import Any, Dict
from copy import deepcopy

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler


class RandomForestModel(MLModel):
    """
    Knowledge Generalization Model backed by a RandomForest algorithm
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data: an dictionary with key `x` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        if self.stats["scaler"] is not None:
            x = self.stats["scaler"].transform(input_data["x"])
        else:
            x = input_data["x"]
        return {"predictions": self.base_model.predict(x)}

    def predict_proba(self, input_data: Dict) -> Dict:
        if self.stats["scaler"] is not None:
            x = self.stats["scaler"].transform(input_data["x"])
        else:
            x = input_data["x"]
        return {"predictions": self.base_model.predict_proba(x)}


class RandomForestModeler(MLModeler):
    """
    Knowledge Generalization Modeler backed by a RandomForest algorithm.
    """

    def __init__(self, model_class=RandomForestModel):
        self.model_class = model_class
        self.stats = {}

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        x, y = prepared_data["x"], prepared_data["y"]
        x = self.preprocess(x)
        model = RandomForestClassifier(max_depth=20, random_state=1)
        model.fit(x, y)
        return model

    def preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)


class LogisticRegressionModel(MLModel):
    """
    Knowledge Generalization Model backed by an Logistic Regression algorithm
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data: an dictionary with key `x` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        if self.stats["scaler"] is not None:
            x = self.stats["scaler"].transform(input_data["x"])
        else:
            x = input_data["x"]
        return {"predictions": self.base_model.predict(x)}

    def predict_proba(self, input_data: Dict) -> Dict:
        if self.stats["scaler"] is not None:
            x = self.stats["scaler"].transform(input_data["x"])
        else:
            x = input_data["x"]
        return {"predictions": self.base_model.predict_proba(x)}


class LogisticRegressionModeler(MLModeler):
    """
    Knowledge Generalization Modeler backed by a AdaBoost algorithm.
    """

    def __init__(self, model_class=LogisticRegressionModel):
        self.model_class = model_class
        self.stats = {}

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        x, y = prepared_data["x"], prepared_data["y"]
        x = self.preprocess(x)
        model = LogisticRegression()
        model.fit(x, y)
        return model

    def preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)
