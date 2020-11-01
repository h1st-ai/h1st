import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import h1st as h1
audit = h1.Auditable()
# collect = h1.Describable()


class WineQuality(h1.MLModel):
    def __init__(self):
        super().__init__()
        self.dataset_name = "WineQuality"
        self.dataset_description = "The dataset is related to red variants of the Portuguese `Vinho Verde` wine.\
             The task is to determine the `Quality` of the wine based on 11 physicochemical tests as input."

        self.label_column = "Quality"
        self.base_model = self._build_base_model()
        self.test_size = 0.2

    # @audit
    @h1.Explainable
    def load_data(self):
        path = os.path.dirname(__file__)
        filename = os.path.join(path, "../data/wine_quality.csv")
        df = pd.read_csv(filename)
        df["quality"] = df["quality"].astype(int)
        for old_name in df.columns:
            df = df.rename(columns={old_name: old_name.replace(" ", "_")},
                           inplace=False)
        return df.reset_index(drop=True)

    # def explore_data(self, data):
    #     data["quality"].hist()
    #     plt.title("Wine Quality Rating Output Labels Distribution")
    #     plt.show()

    # @audit
    # @h1.Describable
    @h1.Explainable
    def prep(self, loaded_data):
        """
        Prepare data for modelling
        :param loaded_data: data return from load_data method
        :returns: dictionary contains train data and validation data
        """
        X = loaded_data.drop("quality", axis=1)
        Y = loaded_data["quality"]
        X_train, X_test, Y_train, Y_test = train_test_split(
            X, Y, test_size=self.test_size)
        return {
            "train_df": X_train,
            "test_df": X_test,
            "train_labels": Y_train,
            "test_labels": Y_test,
        }

    # @audit
    @h1.Explainable
    # @h1.Describable
    def train(self, prepared_data):
        X_train, Y_train = prepared_data["train_df"], prepared_data[
            "train_labels"]
        self.base_model.fit(X_train, Y_train)

    def _mean_absolute_percentage_error(self, y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # @audit
    @h1.Explainable
    def evaluate(self, data):
        X_test, y_true = data["test_df"], data["test_labels"]
        y_pred = self.base_model.predict(X_test)
        return {"mape": self._mean_absolute_percentage_error(y_true, y_pred)}

    def predict(self, input_data):
        """
        :params data: data for prediction
        :returns: prediction result as a dictionary
        """
        return self.base_model.predict(np.expand_dims(input_data, axis=0))[0]

    def _build_base_model(self):
        return RandomForestRegressor(max_depth=6,
                                     random_state=0,
                                     n_estimators=10)