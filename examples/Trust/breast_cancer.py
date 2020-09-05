import os
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import h1st as h1


class BreastCancer(h1.Model):
    def __init__(self):
        super().__init__()
        self.dataset_name = "Wisconsin Breast Cancer Dataset"
        self.dataset_description = "The dataset contains 30 features\
            extracted from an image of a fine needle aspirate (FNA)\
             of a breast mass."
        self.label_column = "diagnosis"
        self.model = None
        self.metrics = None
        self.features = None
        self.test_size = 0.2
        self.prepared_data = None

    def load_data(self):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, "data/breast_cancer.csv")
        df = pd.read_csv(filename)
        df["benign"] = (df.diagnosis == "M").astype(int)
        df.drop(["id", "diagnosis"], axis=1, inplace=True)
        return df.reset_index(drop=True)

    def explore_data(self, data):
        pass

    def prep_data(self, data):
        """
        Prepare data for modelling
        :param loaded_data: data return from load_data method
        :returns: dictionary contains train data and validation data
        """


        self.features = [c for c in data.columns if c != "benign"]
        target = "benign"
        X = data[self.features]
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X.values)
        X = pd.DataFrame(data = X, columns = self.features)
        print(X.describe())
        Y = data[target]
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
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, Y_train)
        self.model = model

    def evaluate(self, data):
        X_test, Y_test = data["val_df"], data["val_labels"]
        Y_pred = self.model.predict(X_test)
        self.metrics = {
            "mae": sklearn.metrics.mean_absolute_error(Y_test, Y_pred),
            "auc": roc_auc_score(Y_test, Y_pred),
        }
        return self.metrics

    def predict(self, data):
        return self.model.predict(data)
