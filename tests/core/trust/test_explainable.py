
import numpy as np
import pandas as pd
import lime
import lime.lime_tabular as lt
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score
import matplotlib.pyplot as plt
import sklearn

import h1st as h1
import unittest
from h1st.core.trust.explainable import Explainable
from h1st.core.trust.explainers.shap_explainer import SHAPExplainer
from h1st.core.trust.explainers.lime_explainer import LIMEExplainer

class TestModelExplainDescribe(h1.Model):
    def __init__(self):
        super().__init__()
        self.model = None
        self.features = [
            "fixed acidity",
            "volatile acidity",
            "citric acid",
            "residual sugar",
            "chlorides",
            "free sulfur dioxide",
            "total sulfur dioxide",
            "density",
            "pH",
            "sulphates",
            "alcohol",
        ]
        # self.data_dir = config.DATA_PATH
        self.test_size = 0.2
        self.shap=True
        self.lime=True
        self.verbose=False

        self.load_data()
        self.prep_data()
        self.train(self.prepared_data)
        self.evaluate(self.prepared_data)

    def load_data(self):
        filename = "s3://arimo-pana-cyber/explain_data/winequality_red.csv"
        df = pd.read_csv(filename)
        df["quality"] = df["quality"].astype(int)
        self.data = df

    def explore(self):
        if self.verbose:
            self.data["quality"].hist()
            plt.title("Wine Quality Rating Output Labels Distribution")
            plt.show()

    def prep_data(self):
        """
        Prepare data for modelling
        :param loaded_data: data return from load_data method
        :returns: dictionary contains train data and validation data
        """

        Y = self.data["quality"]
        X = self.data[self.features]
        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=self.test_size
        )

        self.prepared_data = {
            "train_df": X_train,
            "val_df": X_test,
            "train_labels": Y_train,
            "val_labels": Y_test,
        }

        return self.prepared_data

    def train(self, prepared_data):
        X_train, Y_train = prepared_data["train_df"], prepared_data["train_labels"]
        model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
        model.fit(X_train, Y_train)
        self.model = model
        

    def evaluate(self, prepared_data):
        X_test, y_true = prepared_data["val_df"], prepared_data["val_labels"]
        y_pred = self.model.predict(X_test)
        self.metrics = {
            "mae": sklearn.metrics.mean_absolute_error(y_true, y_pred),
        }
        print(self.metrics)

    def predict(self, filename):
        df = pd.read_csv(filename)
        df["quality"] = df["quality"].astype(int)
        input_data = df[self.features]
        return self.model.predict(input_data)

    def describe(self, constituent=h1.Model.Constituency.DATA_SCIENTIST.name, aspect=h1.Model.Aspect.ACCOUNTABLE.name):     
        d = SHAPExplainer(self.model, self.prepared_data, self.metrics, constituent, aspect, self.verbose)      
        return {'shap_explainer':d}

    def explain(self, constituent=h1.Model.Constituency.DATA_SCIENTIST.name, aspect=h1.Model.Aspect.ACCOUNTABLE.name, decision=None):
        e = LIMEExplainer(self.model, self.prepared_data, self.metrics,decision, constituent, aspect, self.verbose)
        return {'lime_explainer':e}
        


class TestExplainable(unittest.TestCase):
    def test_explainable(self):
        e = TestModelExplainDescribe()
        describe = e.describe()
        idx = 1
        sample_input = e.prepared_data['train_df'].iloc[idx], e.prepared_data['train_labels'].iloc[idx]
        explain = e.explain(decision=sample_input)        
        self.assertEquals(len(explain['lime_explainer'].explainer.feature_names), len(e.features))
        self.assertEquals(describe['shap_explainer'].shap_values.shape, e.prepared_data['train_df'].shape)
        self.assertIsInstance(describe, dict)
        self.assertIsInstance(explain, dict)


