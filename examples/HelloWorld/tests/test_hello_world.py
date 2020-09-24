import unittest
from HelloWorld.rule_based_model import RuleBasedModel
from HelloWorld.ml_model import MLModel


class TestHellloWorld(unittest.TestCase):

    def test_rule_based_model(self):
        m = RuleBasedModel()
        xs = list(range(6))
        results = m.predict({"values": xs})
        print(f"RuleBasedModel's predictions for {xs} is {results}")
        self.assertTrue(results["predictions"] == [True, False, True, False, True, False]


    def test_ml_model(self):
        m = MLModel()
        raw_data = m.get_data()
        prepared_data = m.prep(raw_data)
        m.train(prepared_data)
        metric = m.evaluate(prepared_data)
        print("metric = ", str(metric))
        self.assertGreaterEqual(metric, 0.9)
        m.persist()
