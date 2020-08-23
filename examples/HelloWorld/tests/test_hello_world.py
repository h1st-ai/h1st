import unittest
from HelloWorld.models.rule_based_model import RuleBasedModel
from HelloWorld.models.ml_model import MLModel


class TestHellloWorld(unittest.TestCase):

    def test_rule_based_model(self):
        m = RuleBasedModel()
        for value in range(6):
            prediction = m.predict({"value": value})
            print(f"Prediction for {value} is {m.predict({'value': value})}")
            self.assertTrue(prediction == (value % 2 == 0))


    def test_ml_model(self):
        m = MLModel()
        raw_data = m.get_data()
        prepared_data = m.prep_data(raw_data)
        m.train(prepared_data)
        metric = m.evaluate(prepared_data)
        print(f"metric = {metric}")
        self.assertGreaterEqual(metric, 0.9)
