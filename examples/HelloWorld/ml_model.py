"""
This is an example of a very simple H1st ML model.
We demonstrate here how to wrap a ScikitLearn model within an h1.Model
"""

from sklearn import svm, datasets, metrics
import h1st as h1


class MLModel(h1.MLModel):
    def __init__(self):
        # This is the native SKLearn model
        # H1st can automatically save/load this "self.model" property if it's a SKlearn or tf.keras.Model
        self.model = svm.SVC(gamma=0.001, C=100.)

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
        self.model.fit(prepared_data["train_x"], prepared_data["train_y"])

    def evaluate(self, data):
        pred_y = self.predict({"x": data["test_x"]})
        # self.metrics can also be persisted automatically by H1st
        self.metrics = metrics.accuracy_score(data["test_y"], pred_y)
        return self.metrics

    def predict(self, input_data: dict) -> dict:
        """
        We expect an array of input data rows in the "x" field of the input_data dict
        """
        return self.model.predict(input_data["x"])

if __name__ == "__main__":
    h1.init(MODEL_REPO_PATH=".models")
    
    m = MLModel()
    raw_data = m.get_data()
    print(raw_data)

    prepared_data = m.prep(raw_data)
    print(prepared_data['train_x'].shape)
    print(prepared_data['test_x'].shape)
    
    m.train(prepared_data)
    m.evaluate(prepared_data)
    print("accuracy_score = %.4f" % m.metrics)

    version_id = m.persist()
    print("Persisted to version_id = %s" % version_id)
    m = MLModel().load(version_id)
    print(m.metrics)

