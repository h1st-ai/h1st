from typing import Dict, Any

import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression

import __init__
from h1st.model.kgen_modeler import KGenModeler
from h1st.model.ml_model import MLModel


class MyGenModeler(KGenModeler):
    def __init__(self):
        self.stats = {}

    def preprocess(self, data: pd.DataFrame) -> Any:
        self.stats['scaler'] = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        return self.stats['scaler'].fit_transform(data) 
    
    def train(self, data: Dict[str, Any]) -> Any:
        X, y = data['train_x'], data['train_y']
        model = LogisticRegression(random_state=0)
        model.fit(X, y)
        return model
    
    def build(self, data: Dict[str, Any]) -> MLModel:
        X_train, y_train = (data['X_train'], data['y_train'])            
        
        X_train = self.preprocess(X_train)
            
        base_model = self.train({
            'train_x': X_train,
            'train_y': y_train
        })
        my_gen = self.model_class()
        my_gen.base_model = base_model

        # Pass stats to the model
        if self.stats:
            my_gen.stats = self.stats.copy()
        # Compute metrics and pass to the model
#         ml_model.metrics = self.evaluate(data, ml_model)
        return my_gen