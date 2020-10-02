import os
import logging
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import pandas as pd

from sklearn.preprocessing import RobustScaler
from sklearn import svm
from sklearn.metrics import accuracy_score

import h1st as h1
from examples.Ensemble import config
from examples.Ensemble.utils import prepare_train_test_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TensorflowMLPClassifier(h1.Model):
    def __init__(self):    
        self.model = self.build_tf_architecture(units=16, num_class=config.NUM_CLASS)

    def build_tf_architecture(self, units, num_class):
        inputs = tf.keras.Input(shape=(len(config.DATA_FEATURES)))
        x = tf.keras.layers.Dense(units, activation=tf.nn.selu)(inputs)
        x = tf.keras.layers.Dense(units, activation=tf.nn.selu)(x)
        outputs = tf.keras.layers.Dense(num_class, activation=tf.nn.softmax)(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model

    def load_data(self):
        df = pd.read_excel(config.DATA_PATH, header=1)
        return df

    def prep(self, loaded_data):
        return prepare_train_test_data(loaded_data)

    def train(self, prepared_data):
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        self.stats = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False).fit(X_train)
        X_train = self.stats.transform(X_train)
        self.model.compile(
            optimizer=tf.optimizers.Adam(learning_rate=0.01, clipnorm=1.),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(),
            metrics=["accuracy"])
        self.model.fit(X_train, y_train, epochs=50, batch_size=1024, verbose=0)

    def evaluate(self, prepared_data):
        X_test = prepared_data['X_test']
        y_test = prepared_data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']
        logger.info('%s, %s', y_test.shape, y_pred.shape)
        self.metrics = {'accuracy': accuracy_score(y_test, y_pred)}
        return self.metrics        

    def predict(self, input_data):
        X = input_data['X']
        X = self.stats.transform(X)
        predictions = np.argmax(self.model.predict(X), axis=-1)
        predictions = np.reshape(predictions, [len(predictions), -1])
        return {'predictions': predictions}