import numpy as np
import pandas as pd
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score

from h1st.core.model import Model


class StackEnsemble(Model):
    def __init__(self, ensembler, sub_models):
        self.metrics = {}
        self.model = ensembler
        self._sub_models = sub_models

    def preprocess(self, X, training=False): 
        # TODO: how can we know user’s key of data (ex. X)
        # TODO: how can we know user’s key of return of predict (ex. predictions)

        # Feed input_data to each sub-model and get predictions 
        predictions = [m.predict({'X': X})['predictions'] for m in self._sub_models]
        
        # Combine raw_data and predictions
        X = np.hstack([X] + predictions)

        # Scale data with RobustScaler
        if training:
            self.stats = RobustScaler(
                quantile_range=(5.0, 95.0), with_centering=False).fit(X)
        X = self.stats.transform(X)
        return X

    def train(self, prepared_data: dict):
        X_train, y_train = (prepared_data['X_train'], prepared_data['y_train'])
        X_train = self.preprocess(X_train, training=True)
        self.model.fit(X_train, y_train)

    def predict(self, data: dict):
        X = data['X']
        X = self.preprocess(X)
        return {'predictions': self.model.predict(X)}


class StackEnsembleClassifier(StackEnsemble):
    def evaluate(self, data: dict, metrics=['accuracy']):
        X_test, y_test = data['X_test'], data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']
        
        self.metrics['confusion_matrix'] = confusion_matrix(y_test, y_pred)
        self.metrics['recall'], self.metrics['recall'], \
        self.metrics['f1'] , self.metrics['support'] \
            = precision_recall_fscore_support(y_test, y_pred)
        if 'accuracy' in metrics:
            self.metrics['accuracy'] = accuracy_score(y_test, y_pred)
        return self.metrics


class RandomForestStackEnsembleClassifier(StackEnsembleClassifier):
    def __init__(self, sub_models: list):
        ensembler = MultiOutputClassifier(RandomForestClassifier(
            n_jobs=-1, max_depth=4, random_state=42))
        super().__init__(ensembler, sub_models)

