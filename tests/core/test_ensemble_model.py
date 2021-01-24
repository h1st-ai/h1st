import math
import pandas as pd
from unittest import TestCase, skip
from sklearn.model_selection import train_test_split
import h1st.core as h1
import examples.Ensemble.config as config
from examples.Ensemble.sklearn_smv_classifier import SklearnSVMClassifier
from examples.Ensemble.tensorflow_mlp_classifier import TensorflowMLPClassifier

class RandomForestClassifierStackEnsemble(h1.RandomForestClassifierStackEnsemble):
    def load_data(self,):
        df = pd.read_excel(config.DATA_PATH, header=1)
        return df

    def prep(self, loaded_data):
        df = loaded_data
        X = df[config.DATA_FEATURES].values
        y = df[config.DATA_TARGETS].values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.33, shuffle=True, random_state=10)
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }

class RandomForestClassifierStackEnsembleTestCase(TestCase):
    def test_ensemble(self):
        m1 = SklearnSVMClassifier()
        data = m1.load_data()
        prepared_data = m1.prep(data)
        m1.train(prepared_data)
        m1.evaluate(prepared_data)
        m1.persist('m1')
        self.assertIn('accuracy', m1.metrics)

        m2 = TensorflowMLPClassifier()
        data = m2.load_data()
        prepared_data = m2.prep(data)
        m2.train(prepared_data)
        m2.evaluate(prepared_data)
        m2.persist('m2')
        self.assertIn('accuracy', m2.metrics)

        ensemble = RandomForestClassifierStackEnsemble([
            SklearnSVMClassifier().load('m1'),
            TensorflowMLPClassifier().load('m2')
        ])
        data = ensemble.load_data()
        prepared_data = ensemble.prep(data)
        ensemble.train(prepared_data)
        ensemble.evaluate(prepared_data)
        ensemble.persist('ensemble')
        self.assertIn('accuracy', ensemble.metrics)

        # ensure performance of ensemble is better than any sub models
        self.assertGreaterEqual(ensemble.metrics['accuracy'], m1.metrics['accuracy']-0.02)
        self.assertGreaterEqual(ensemble.metrics['accuracy'], m2.metrics['accuracy']-0.02)


        