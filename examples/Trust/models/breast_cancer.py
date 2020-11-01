import os
import pandas as pd
import sklearn
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import h1st as h1


class BreastCancer(h1.MLModel):
    def __init__(self):
        super().__init__()
        self.dataset_name = "Wisconsin Breast Cancer Dataset"
        self.dataset_description = "The dataset contains 30 features\
            extracted from an image of a fine needle aspirate (FNA)\
             of a breast mass."

        self.label_column = "benign"
        self.base_model = self._build_base_model()

    @h1.Explainable
    def load_data(self):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, "../data/breast_cancer.csv")
        df = pd.read_csv(filename)
        df["benign"] = (df.diagnosis == "M").astype(int)
        df.drop(["id", "diagnosis"], axis=1, inplace=True)
        for old_name in df.columns:
            df = df.rename(columns={old_name: old_name.replace(" ", "_")},
                           inplace=False)
        return df.reset_index(drop=True)

    # def explore_data(self, data):
    #     pass
    @h1.Explainable
    def prep(self, data):
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
        X = pd.DataFrame(data=X, columns=self.features)
        Y = data[target]
        X_train, X_test, Y_train, Y_test = train_test_split(X,
                                                            Y,
                                                            test_size=0.2)
        return {
            "train_df": X_train,
            "test_df": X_test,
            "train_labels": Y_train,
            "test_labels": Y_test,
        }

    @h1.Explainable
    def train(self, prepared_data):
        X_train, Y_train = prepared_data["train_df"], prepared_data[
            "train_labels"]
        self.base_model.fit(X_train, Y_train)

    @h1.Explainable
    def evaluate(self, data):
        X_test, Y_test = data["test_df"], data["test_labels"]
        Y_pred = self.base_model.predict(X_test)
        return {
            "mae": sklearn.metrics.mean_absolute_error(Y_test, Y_pred),
            "auc": roc_auc_score(Y_test, Y_pred),
        }

    def predict(self, input_data):
        """
        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        return self.base_model.predict(np.expand_dims(input_data, axis=0))[0]

    def _build_base_model(self):
        return RandomForestClassifier(max_depth=6,
                                      random_state=0,
                                      n_estimators=20)