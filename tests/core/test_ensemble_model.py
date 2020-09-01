import math
import pandas as pd
from unittest import TestCase, skip
from sklearn.model_selection import train_test_split
from h1st import RandomForestStackEnsembleClassifier
import h1st as h1
import examples.Ensemble.config as config
from examples.Ensemble.models.submodel_examples import SK_SVM_Classifier, TF_FC_Classifier

class RandomForestStackEnsembleClassifier(RandomForestStackEnsembleClassifier):
    def load_data(self,):
        df = pd.read_excel(config.DATA_PATH, header=1)
        return df

    def prep_data(self, loaded_data):
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

class RandomForestStackEnsembleClassifierTestCase(TestCase):
    def test_ensemble(self):
        m1 = SK_SVM_Classifier()
        data = m1.load_data()
        prepared_data = m1.prep_data(data)
        m1.train(prepared_data)
        m1.evaluate(prepared_data)
        m1.persist('m1')
        self.assertIn('accuracy', m1.metrics)

        m2 = TF_FC_Classifier()
        data = m2.load_data()
        prepared_data = m2.prep_data(data)
        m2.train(prepared_data)
        m2.evaluate(prepared_data)
        m2.persist('m2')
        self.assertIn('accuracy', m2.metrics)

        ensemble = RandomForestStackEnsembleClassifier([
            SK_SVM_Classifier().load('m1'),
            TF_FC_Classifier().load('m2')
        ])
        data = ensemble.load_data()
        prepared_data = ensemble.prep_data(data)
        ensemble.train(prepared_data)
        ensemble.evaluate(prepared_data)
        ensemble.persist('ensemble')
        self.assertIn('f1', ensemble.metrics)

        # ensure performance of ensemble is better than any sub models
        self.assertGreaterEqual(ensemble.metrics['f1'], m1.metrics['f1'])
        self.assertGreaterEqual(ensemble.metrics['f1'], m2.metrics['f1'])


        