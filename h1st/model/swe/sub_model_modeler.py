from typing import Any, Dict
from copy import deepcopy

import pandas as pd
from sklearn.ensemble import RandomForestClassifier as SKRandomForestClassifier
from sklearn import metrics

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler


class RandomForestClassifier(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data['X'])
        return {'predictions': y}


class RandomForestClassifierModeler(MLModeler):
    def __init__(self, model_class=RandomForestClassifier):
        self.model_class = model_class
        self.stats = {}
    
    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        X, y_true = data['X_test'], data['y_test']
        y_pred = pd.Series(model.predict({'X': X, 'y': y_true})['predictions'])
        return {'r2_score': metrics.r2_score(y_true, y_pred)}

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data['X_train'], data['y_train']
        model = SKRandomForestClassifier()
        model.fit(X, y)
        return model

