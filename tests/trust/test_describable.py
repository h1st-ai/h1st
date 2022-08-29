import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from h1st.model.ml_model import MLModel


class DescribableModel(MLModel):
    def __init__(self):
        super().__init__()
        self.dataset_name = "WineQuality"
        self.dataset_description = "The dataset is related to red variants of the Portuguese `Vinho Verde` wine.\
             The task is to determine the `Quality` of the wine based on 11 physicochemical tests as input."
        self.label_column = "Quality"
        self._native_model = RandomForestRegressor(max_depth=6, random_state=0, n_estimators=10)
        self.metrics = None
        self.features = None
        self.test_size = 0.2
        self.prepared_data = None

    def load_data(self):
        filename = "./tests/trust/wine_quality.csv"
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
        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=self.test_size
        )
        self.prepared_data = {
            "train_df": x_train,
            "test_df": x_test,
            "train_labels": y_train,
            "test_labels": y_test,
        }
        return self.prepared_data

    def train(self, prepared_data):
        x_train, y_train = prepared_data["train_df"], prepared_data["train_labels"]
        self._native_model.fit(x_train, y_train)

    def _mean_absolute_percentage_error(self, y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def evaluate(self, data):
        x_test, y_true = data["test_df"], data["test_labels"]
        y_pred = self._native_model.predict(x_test)
        self.metrics = {
            "mape": self._mean_absolute_percentage_error(y_true, y_pred)
        }
        return self.metrics


class TestDescribable:
    def test_describable(self):
        m = DescribableModel()
        data = m.load_data()
        prepared_data = m.prep_data(data)
        m.train(prepared_data)
        describer = m.describe()
        assert describer.shap_describer.shap_values.shape == m.prepared_data['train_df'].shape
        assert isinstance(describer, object)
