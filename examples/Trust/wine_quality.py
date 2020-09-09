import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import sklearn
import h1st as h1


class WineQuality(h1.MLModel):
    def __init__(self):
        super().__init__()
        self.dataset_name = "WineQuality"
        self.dataset_description = "The dataset is related to red variants of the Portuguese `Vinho Verde` wine.\
             The task is to determine the `Quality` of the wine based on 11 physicochemical tests as input."
        self.label_column = "Quality"
        self._native_model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
        self.features = None
        self.metrics = None
        self.test_size = 0.2
        self.prepared_data = None

    def load_data(self):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, "data/wine_quality.csv")
        df = pd.read_csv(filename)
        df["quality"] = df["quality"].astype(int)
        return df.reset_index(drop=True)

    def explore_data(self, data):        
        data["quality"].hist()
        plt.title("Wine Quality Rating Output Labels Distribution")
        plt.show()

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
        # model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
        self._native_model.fit(X_train, Y_train)
        # self.ml_model = model

    # def _mean_absolute_percentage_error(self, y_true, y_pred):
    #     y_true, y_pred = np.array(y_true), np.array(y_pred)
    #     return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # def evaluate(self, data):
    #     X_test, y_true = data["test_df"], data["test_labels"]
    #     y_pred = self.ml_model.predict(X_test)
    #     return {
    #         "mape": self._mean_absolute_percentage_error(y_true, y_pred)
    #     }

    # def predict(self, data):
    #     data["quality"] = data["quality"].astype(int)
    #     input_data = data[self.features]
    #     return self.ml_model.predict(input_data)
