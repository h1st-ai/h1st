import unittest
import h1st as h1

from HelloWorld.rule_based_model import RuleBasedModel
from HelloWorld.ml_model import MLModel
from HelloWorld.graph import create_graph


class TestHellloWorld(unittest.TestCase):

    def test_rule_based_model(self):
        m = RuleBasedModel()
        xs = list(range(6))
        results = m.predict({"values": xs})
        print(f"RuleBasedModel's predictions for {xs} is {results}")
        self.assertTrue(results["predictions"] == [
            {'prediction': True, 'value': 0}, {'prediction': False, 'value': 1}, {'prediction': True, 'value': 2}, {'prediction': False, 'value': 3}, {'prediction': True, 'value': 4}, {'prediction': False, 'value': 5}])

    def test_ml_model(self):
        h1.init(MODEL_REPO_PATH=".models")
        m = MLModel()
        raw_data = m.get_data()
        prepared_data = m.prep(raw_data)

        m.train(prepared_data)
        metric = m.evaluate(prepared_data)
        print("metric = ", str(metric))
        self.assertGreaterEqual(metric, 0.9)

        version_id = m.persist()
        print("Persisted to version_id = %s" % version_id)
        m = MLModel().load(version_id)
        self.assertGreaterEqual(m.metrics, 0.9)

    def test_graph(self):
        graph = create_graph()
        results = graph.predict({"values": range(6)})
        print(results)
        self.assertEqual(results, {'predictions': [{'prediction': True, 'value': 0}, {'prediction': False, 'value': 1}, {'prediction': True, 'value': 2}, {'prediction': False, 'value': 3}, {'prediction': True, 'value': 4}, {'prediction': False, 'value': 5}]})
