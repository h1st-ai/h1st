import unittest
from rule_based_model import RuleBasedModel

class TestHellloWorld(unittest.TestCase):

    def test_rule_based_model(self):
        m = RuleBasedModel()
        for value in range(6):
            prediction = m.predict({"value": value})
            print("Prediction for " + str(value) + " is " + str(m.predict({"value": value})))
            self.assertTrue(prediction == (value % 2 == 0))