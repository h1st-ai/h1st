"""
This is an example of a very simple H1st ML model.
We demonstrate here how to wrap a ScikitLearn model within an h1.Model
"""

from sklearn import svm, datasets, metrics
import h1st as h1


class MLModel(h1.MLModel):
    def __init__(self):
        self._native_model = svm.SVC(gamma=0.001, C=100.)

    def get_data(self):
        digits = datasets.load_digits()
        return {
            "x": digits.data,
            "y": digits.target
        }

    def explore_data(self, data):
        pass

    def prep(self, data):
        x = data["x"]
        y = data["y"]
        num_tests = 10
        return {
            "train_x": x[num_tests:],
            "train_y": y[num_tests:],
            "test_x": x[0:num_tests],
            "test_y": y[0:num_tests]
        }

    def train(self, prepared_data):
        self._native_model.fit(prepared_data["train_x"], prepared_data["train_y"])

    def evaluate(self, data):
        pred_y = self.predict({"x": data["test_x"]})
        metric = metrics.accuracy_score(data["test_y"], pred_y)
        return metric

    def predict(self, input_data: dict) -> dict:
        """
        We expect an array of input data rows in the "x" field of the input_data dict
        """
        return self._native_model.predict(input_data["x"])
