import __init__
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler

from h1st.model.ensemble.ensemble_modeler import EnsembleModeler
from h1st.model.model import Model
from h1st.model.ml_model import MLModel


class MyEnsembleModeler(EnsembleModeler):
    def __init__(self, sub_models: List[Model], **kwargs):
        self.stats = {}
        self._sub_models = sub_models
        self._submodel_predict_input_key = kwargs.get(
            'submodel_predict_input_key', 'X')
        self._submodel_predict_output_key = kwargs.get(
            'submodel_predict_output_key', 'predictions')            

    def _get_submodels_prediction(self, X: Any) -> Any:
        preds = []
        for m in self._sub_models:
            pred = m.predict({self._submodel_predict_input_key: X})
            output = pred.get(self._submodel_predict_output_key)
            if output is not None:
                preds.append(output)
        return np.hstack(preds)            

    def _preprocess(self, data: pd.DataFrame):
        self.stats['scaler'] = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        return self.stats['scaler'].fit_transform(data)         
  
    def _train(self, data: Dict[str, Any]) -> Any:
        X, y = data['train_x'], data['train_y']            
        model = RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42)
        model.fit(X, y)
        return model

    def build(self, data: Dict[str, Any]) -> MLModel:
        X_train, y_train = (data['X_train'], data['y_train'])    

        # get submodel predictions
        predictions = self._get_submodels_prediction(X_train)
            
        # create a dataframe from submodel predictions
        df_submodel_labels = pd.DataFrame(
            predictions, columns=[f'model_{i}' for i in range(len(self._sub_models))])
        
        # merge X_train and df_submodel_labels
        X_train_with_submodel_labels = X_train.join(df_submodel_labels)
        
        # preprocess whole features of ensemble model
        X_train_with_submodel_labels = self._preprocess(
            X_train_with_submodel_labels)
        
        # train base_model of ensemble
        base_model = self._train({
            'train_x': X_train_with_submodel_labels,
            'train_y': y_train
        })
        my_ensemble = self.model_class()
        my_ensemble.base_model = base_model

        # Pass stats to the model
        if self.stats:
            my_ensemble.stats = self.stats.copy()
            
        return my_ensemble


class MyEnsemble(MLModel):
    def predict(self, data):
        pass


