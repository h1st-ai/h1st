
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

class TestModelExplainable(h1.Model):
    def __init__(self):
        super().__init__()
        self.dataset_name = "WineQuality"
        self.dataset_description = "The dataset is related to red variants of the Portuguese `Vinho Verde` wine.\
             The task is to determine the `Quality` of the wine based on 11 physicochemical tests as input."
        self.label_column = "Quality"
        self.ml_model = None
        self.features = None
        self.metrics = None
        self.test_size = 0.2
        self.prepared_data = None
        
        def load_data(self):
            filename = "s3://arimo-pana-cyber/explain_data/winequality_red.csv"
            df = pd.read_csv(filename)
            df["quality"] = df["quality"].astype(int)
            return df.reset_index(drop=True)

    def prep_data(self, data):
        """
        Prepare data for modelling
        :param loaded_data: data return from load_data method
        :returns: dictionary contains train data and validation data
        """
        X = data.drop("quality", axis=1)
        Y = data["quality"]
        self.features = list(X.columns)
        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=self.test_size
        )
        self.prepared_data = {
            "train_df": X_train,
            "test_df": X_test,
            "train_labels": Y_train,
            "test_labels": Y_test,
        }
        return self.prepared_data

    def train(self, prepared_data):
        X_train, Y_train = prepared_data["train_df"], prepared_data["train_labels"]
        model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
        model.fit(X_train, Y_train)
        self.ml_model = model
        
class TestExplainable(unittest.TestCase):
    def test_explainable(self):
        m = TestModelExplainable()
        data = m.load_data()
        prepared_data = m.prep_data(data)
        m.train(prepared_data)
        idx = 4
        decision_input = m.prepared_data["train_df"].iloc[idx]
        explainer = m.explain(decision_input=decision_input)
        self.assertEquals(len(explainer.lime_explainer.explainer.feature_names), len(m.features))
        self.assertIsInstance(explainer, object)


