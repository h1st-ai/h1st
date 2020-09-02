import os
import logging
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn import svm
from sklearn.metrics import accuracy_score

import h1st as h1
from examples.Ensemble import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SK_SVM_Classifier(h1.Model):
    def __init__(self):
        self.model = svm.SVC()
    
    def load_data(self):
        df = pd.read_excel(config.DATA_PATH, header=1)
        return df
    
    def explore(self, loaded_data):
        df = loaded_data
        for target in config.DATA_TARGETS:
            df[target].hist()
            plt.show()

    def prep_data(self, loaded_data):
        df = loaded_data
        X = df[config.DATA_FEATURES].values
        y = df[config.DATA_TARGETS].values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.33, shuffle=True, random_state=10)
        logger.info('%s, %s, %s, %s', X_train.shape, X_test.shape, y_train.shape, y_test.shape)
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }

    def train(self, prepared_data):
        X_train = prepared_data['X_train']
        y_train = prepared_data['y_train']
        self.stats = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False).fit(X_train)
        X_train = self.stats.transform(X_train)
        self.model.fit(X_train, y_train)

    def evaluate(self, prepared_data):
        X_test = prepared_data['X_test']
        y_test = prepared_data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']
        self.metrics = {'accuracy': accuracy_score(y_test, y_pred)}
        return self.metrics

    def predict(self, input_data):
        X = input_data['X']
        X = self.stats.transform(X)
        predictions = self.model.predict(X)
        predictions = np.reshape(predictions, [len(predictions), -1])
        return {'predictions': predictions}


class TF_FC_Classifier(h1.Model):
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

    def prep_data(self, loaded_data):
        df = loaded_data
        X = df[config.DATA_FEATURES].values
        y = df[config.DATA_TARGETS].values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.33, shuffle=True, random_state=10)
        logger.info('%s, %s, %s, %s', X_train.shape, X_test.shape, y_train.shape, y_test.shape)
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }

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