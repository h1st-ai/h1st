import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score

from h1st.core.model import Model
from h1st.core.exception import ModelException


class Ensemble(Model):
    """
    Base Ensemble class to implement various ensemble classes in the future
    even though we currently only have StackEnsemble.
    """

    def __init__(self, ensembler, sub_models: List[Model]):
        """
        :param ensembler: ensembler model, currently it is sklearn's MultiOutputClassifier
            when framework supports StackEnsembleRegressor,
            ensembler could be either MultiOutputClassifier or another specific base model 
        :param sub_models: list of h1st.Model participating in the stack ensemble
        """
        self.model = ensembler
        self._sub_models = sub_models


class StackEnsemble(Ensemble):
    """
    Base StackEnsemble class to implement StackEnsemble classifiers or regressors.
    """

    def __init__(self, ensembler: MultiOutputClassifier, sub_models: List[Model]):
        """
        :param ensembler: ensembler model, currently it is sklearn's MultiOutputClassifier
            when framework supports StackEnsembleRegressor,
            ensembler could be either MultiOutputClassifier or another specific base model 
        :param sub_models: list of h1st.Model participating in the stack ensemble
        """
        self.model = ensembler
        self._sub_models = sub_models

    def _preprocess(self, X: Any) -> Any:
        """
        Predicts all sub models then merge input raw data with predictions for ensembler's training or prediction
        :param X: raw input data
        """

        # Feed input_data to each sub-model and get predictions 
        predictions = [m.predict({'X': X})['predictions'] for m in self._sub_models]
        
        # Combine raw_data and predictions
        return np.hstack([X] + predictions)

    def train(self, prepared_data: Dict):
        """
        Trains ensembler with input is merging raw data 'X_train' and predictions of sub models, with targets 'y_train'
        :param prepared_data: output of prep_data() implemented in subclass of StackEnsemble, its structure must be this dictionary
            {
                'X_train': ...,
                'X_test': ...,
                'y_train': ...,
                'y_test': ...
            }
        """
        X_train, y_train = (prepared_data['X_train'], prepared_data['y_train'])
        
        X_train = self._preprocess(X_train)
        scaler = RobustScaler(quantile_range=(5.0, 95.0), with_centering=False)
        self.stats = scaler.fit(X_train)
        X_train = self.stats.transform(X_train)

        self.model.fit(X_train, y_train)

    def predict(self, data: Dict) -> Dict:
        """
        Returns predictions of ensembler model for input raw data combining with predictions from sub models

        This method will raise ModelException if ensembler model has not been trained.

        :param data: must be a dictionary {'X': ...}, with X is raw data
        :return:
            output will be a dictionary {'predictions': ....}
        """
        if not self.stats:
            raise ModelException('This model has not been trained')

        X = self._preprocess(data['X'])
        X = self.stats.transform(X)
        return {'predictions': self.model.predict(X)}


class StackEnsembleClassifier(StackEnsemble):
    """StackEnsemble classifier

    This is the base class for stack ensemble classifiers
    """

    def evaluate(self, data: Dict, metrics: List[str]=None) -> Dict:
        """
        Evaluates for the test data
        :param data: a dictionary {'X_test': ..., 'y_test': ...}
        :param metrics: list of metrics to return and to persist later by the model.
            Default value = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']
        
        :return:
            a dictionary containing requested metrics

        """
        def add_metric(name, value):
            if name in metrics:
                self.metrics[name] = value

        if not metrics:
            metrics = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']

        X_test, y_test = data['X_test'], data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']     
        
        precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred)

        add_metric('confusion_matrix', confusion_matrix(y_test, y_pred))        
        add_metric('precision', precision)
        add_metric('recall', recall)
        add_metric('f1', f1)
        add_metric('support', support)
        add_metric('accuracy', accuracy_score(y_test, y_pred))

        return self.metrics


class RandomForestStackEnsembleClassifier(StackEnsembleClassifier):
    """
    A ready to use StackEnsemble for classifier with ensembler is a sklearn's MultiOutputClassifier using RandomForestClassifier

    Each sub model must be a subclass of h1.Model and its .predict() method will receive an input data as dictionary and return a dictionary

    .. code-block:: python
        :caption: Sub model for a StackEnsemble Example

        class Model1(h1.Model):
            def predict(self, data):
                X = data['X']
                ...
                return {'predictions': }

    .. code-block:: python
        :caption: RandomForestStackEnsembleClassifier usage Example

        class Model2(h1.Model):
                def predict(self, data):
                    X = data['X']
                    ...
                    return {'predictions': }

        class RandomForestStackEnsembleClassifier(StackEnsembleClassifier):
            def __init__(self):
                super().__init__([
                    Model1().load('version_of_model_1'),
                    Model2().load('version_of_model_2')
                ])

            def load_data(self,):
                ...
                return loaded_data

            def prep_data(self, loaded_data):
                ...
                return prepared_data

        m1 = Model1()
        loaded_data = m1.load_data()
        prepared_data = m1.prep_data(loaded_data)
        m1.train(prepared_data)
        m1.persist('version_of_model_1')

        m2 = Model2()
        loaded_data = m2.load_data()
        prepared_data = m2.prep_data(loaded_data)
        m2.train(prepared_data)
        m2.persist('version_of_model_2')

        ensemble = RandomForestStackEnsembleClassifier(
            [Model1().load('version_of_model_1'),
             Model2().load('version_of_model_2')])
        loaded_data = ensemble.load_data()
        prepared_data = ensemble.prep_data(loaded_data)
        ensemble.train(prepared_data)
        ensemble.persist('version_of_model_ensemble')
        ensemble.predict(...)
    """
    def __init__(self, sub_models: List[Model]):
        super().__init__(
            MultiOutputClassifier(RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42)),
            sub_models
        )
