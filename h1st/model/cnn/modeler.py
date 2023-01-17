from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from tensorflow.keras import layers
import config

import numpy as np
import pandas as pd
import pickle
import tensorflow as tf

from typing import Any, Dict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

class CNNClassifierModeler(MLModeler):

    model_class = CNNClassifierModel

    def __init__(self, n_classes=5, classifier_activation='softmax', n_wrap=48,
                 learning_rate=0.001, batch_size=10, epochs=200):
        '''
        initialize CNN Classifier Modeler
        :param n_classes: number of classes to classify
        :param classifier_activation: activiation function to use for classification
        :param n_warp: number of columns at which to wrap a sample row to create a 2D matrix
        '''
        self.model_class = CNNFailureClassifierModel
        self.stats = {
            'n_classes': n_classes,
            'classifier_activation':  classifier_activation,
            'n_wrap': n_warp,
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            'epochs': epochs,
        }
        self.metrics = {}

    def build_tensorflow_cnn_classifier(self, input_shape, n_classes,
                                        classifier_activation):
        inputs = tf.keras.Input(shape=input_shape)
        x = self.cnn_block(
            inputs, 16, kernel_size=3, stride=3, name='block1', conv_shortcut=True
        )
        x = self.cnn_block(x, 32, kernel_size=3, stride=3, name='block2', conv_shortcut=True)
        x = self.cnn_block(x, 64, kernel_size=3, stride=3, name='block3', conv_shortcut=True)
        x = layers.Flatten()(x)
        outputs = layers.Dense(
            n_classes, activation=classifier_activation, name=self.output_key
        )(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs, name="test_model")
        return model
    
    def cnn_block(self, x, filters, kernel_size=3, stride=1, name=None, conv_shortcut=False):
        bn_axis = 3
        preact = layers.BatchNormalization(
            axis=bn_axis, epsilon=1.001e-5, name=name + '_preact_bn'
        )(x)
        preact = layers.Activation('relu', name=name + '_preact_relu')(preact)

        if conv_shortcut:
            shortcut = layers.Conv2D(2 * filters, 1, strides=stride, name=name + '_0_conv')(
                preact
            )
        else:
            shortcut = layers.MaxPooling2D(1, strides=stride)(x) if stride > 1 else x

        x = layers.Conv2D(filters, 1, strides=1, use_bias=False, name=name + '_1_conv')(
            preact
        )
        x = layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(
            x
        )
        x = layers.Activation('relu', name=name + '_1_relu')(x)
        x = layers.ZeroPadding2D(padding=((1, 1), (1, 1)), name=name + '_2_pad')(x)
        x = layers.Conv2D(
            filters, kernel_size, strides=stride, use_bias=False, name=name + '_2_conv'
        )(x)
        x = layers.BatchNormalization(axis=bn_axis, epsilon=1.001e-5, name=name + '_2_bn')(
            x
        )
        x = layers.Activation('relu', name=name + '_2_relu')(x)
        x = layers.Conv2D(2 * filters, 1, name=name + '_3_conv')(x)
        x = layers.Add(name=name + '_out')([shortcut, x])
        return x

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        """
        Implement logic of training the base/native model
        :param prepared_data: prepared data
        """
        X, norm = self.prep(prepared_data['X_train'])
        transformed_data = {'X_train': X, 'y_train': prepared_data['y_train']}
        print('>>> Training dataset size: ', X.shape)
        print('>>> Training Category size: ', y.shape)
        self.stats['input_shape'] = X.shape[1:]
        self.stats['input_columns'] = prepared_data['X_train'].columns

        if 'X_test' in prepared_data:
            X_test, _ = self.prep(prepared_data['X_test'], norm_vector=norm,
                                  input_columns=self.stats['input_columns'])
            transformed_data['X_test'] = X_test
            transformed_data['y_test'] = prepared_data['y_test']
            print('>>> Test dataset size: ', X_test.shape)
            print('>>> Test Category size: ', y_test.shape)

        self.train(transformed_data)
        self.evaluate()

    def prep(self, X, norm_vector=None, input_columns=None) -> (np.array, np.array):
        """
        normalize and wrap data into 4D matrix for CNN training
        """
        if input_columns is not None:
            X = X[input_columns]

        X = X.to_numpy()
        # Normalize
        if norm_vector is None:
            norm_vector = np.abs(X).max(axis=0)

        X_tmp_norm = X / norm_vector

        # Reshape into 2D per sample. So shape is [N_sample, N_feature, N_time]
        # or [N_sample, N_time, N_feature]
        N_sample = X.shape[0]
        N_features = X.shape[1]
        N_wrap = self.stats['n_wrap']
        N_row = int(N_features / N_wrap)
        if N_features / N_wrap != N_row:
            raise ValueError(f'Odd number of columns in input. '
                             f'Cannot wrap row into 2D matrix'
                             f'Found {N_features} columns, Expected '
                             f'{N_row*N_wrap} based on wrap value of {N_wrap}')

        X_norm = X_tmp_norm.reshape([-1, N_row, N_wrap])

        # Expand to 4D for CNN
        X_out = np.expand_dims(X_norm, axis=3)
        return X_out, norm_vector

    def train(self, prepared_data: dict):
        """
        Implement logic of training model
        :param prepared_data: prepared data from ``prep`` method
        """
        # grab hyperparams
        input_shape = self.stats['input_shape']
        learning_rate = self.stats['learning_rate']
        n_classes = self.stats['n_classes']
        classifier_activation = self.stats['classifier_activation']
        batch_size = self.stats['batch_size']
        epochs = self.stats['epochs']

        X, y = (prepared_data['X_train'], prepared_data['y_train'])
        if 'X_test' in prepared_data:
            validation_data = (prepared_data['X_test'], prepared_data['y_test'])
        else:
            validation_data = None

        # create model blocks
        self.base_model = self.build_tensorflow_cnn_classifier(
            input_shape, n_classes, classifier_activation
        )

        # compile model
        self.base_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(),
            metrics=["accuracy"])

        # fit model
        self.base_model.fit(X, y,
                            batch_size=batch_size,
                            epochs=epochs,
                            validation_data=(test_x, test_y))

    def evaluate(self, input_data: dict, model: CNNClassifierModel):
        """
        Implement logic to evaluate the model using the prepared_data
        This function will calculate model metrics and store it into self.metrics
        """
        if 'X_test' not in input_data:
            return {}

        predictions = self.model.predict(
            {model.data_key: input_data['X_test']}
        )[model.output_key]
        y_pred = np.argmax(predictions, axis=1)
        print('>>> prediction: ', y_pred)
        y_true = self.prep(self.load_data())['test_y']
        print('>>> true values', y_true)

        self.metrics = {
            "confusion_matrix": confusion_matrix(y_true, y_pred),
            "accuracy": accuracy_score(y_true, y_pred)
        }
        return self.metrics
