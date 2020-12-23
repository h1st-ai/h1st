import os
import logging
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import h1st as h1
from examples.Ensemble import config
from examples.Ensemble.utils import prepare_train_test_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SklearnRFClassifier(h1.MLModel):
    def __init__(self, n_estimators, max_depth, criterion, min_samples_split):
        self.base_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            criterion=criterion,
            min_samples_split=min_samples_split
        )
    
    def load_data(self):
        df = pd.read_excel(config.DATA_PATH, header=1)
        return df
    
    def explore(self, loaded_data):
        df = loaded_data
        for target in config.DATA_TARGETS:
            df[target].hist()
            plt.show()

    def prep(self, loaded_data):
        return prepare_train_test_data(loaded_data)

    def train(self, prepared_data):
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        self.stats = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False).fit(X_train)
        X_train = self.stats.transform(X_train)
        self.base_model.fit(X_train, y_train)

    def evaluate(self, prepared_data):
        X_test = prepared_data['X_test']
        y_test = prepared_data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']
        self.metrics = {'accuracy': accuracy_score(y_test, y_pred)}
        return self.metrics

    def predict(self, input_data):
        X = input_data['X']
        X = self.stats.transform(X)
        predictions = self.base_model.predict(X)
        predictions = np.reshape(predictions, [len(predictions), -1])
        return {'predictions': predictions}

