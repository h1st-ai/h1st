import h1st as h1
import sys


from h1st.core.trust.explainers.shap_explainer import SHAPExplainer
from h1st.core.trust.explainers.lime_explainer import LIMEExplainer

import os
import boto3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score
import matplotlib.pyplot as plt
import sklearn


class WineQualityModel(h1.Model):
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
        self.plot=True

    def load_data(self):
        filename = "s3://arimo-pana-cyber/explain_data/winequality_red.csv"
        df = pd.read_csv(filename)
        df["quality"] = df["quality"].astype(int)
        self.data = df

    def explore(self):
        if self.plot:
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

    def describe(self, constituent=h1.Model.Constituency.DATA_SCIENTIST, aspect=h1.Model.Aspect.ACCOUNTABLE):
        ## TODO: For each pair of constituent and aspect write functions to show relevant information.
        print("Description type: {}"\
            .format(h1.Model.Aspect.ACCOUNTABLE.name))
        print("Targeted Constituent: {}"\
            .format(h1.Model.Constituency.DATA_SCIENTIST.name))
        print("Model Metrics : {}".format(self.metrics))
        
        print("Size of the WineQuality dataset: {}".format(self.data.shape[0]))
        print("Number of features of the WineQuality dataset: {}".format(len(self.features)))

        if self.shap:
            print("Overview of the features that are most important for the WineQualityModel. Seen in the plot are SHAP values of every feature for every sample.The plot below sorts features by the sum of SHAP value magnitudes over all samples, and uses SHAP values to show the distribution of the impacts each feature has on the model output. The color represents the feature value (red high, blue low). This reveals for example that a high alcohol increases the predicted wine quality.".format())
            d = SHAPExplainer(self.model, self.prepared_data, self.plot)      
            return {'shap_values':d.shap_values}

    def explain(self, constituent=h1.Model.Constituency.DATA_SCIENTIST, aspect=h1.Model.Aspect.ACCOUNTABLE, decision=None):
        e = LIMEExplainer(self.model, self.prepared_data, decision, self.plot)
        return {'lime_predictions':e.decision_explainer.as_list()}

