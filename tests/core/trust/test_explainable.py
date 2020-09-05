import unittest
from h1st.core.trust.explainable import Explainable


class SomeExplainableThing(Explainable):
    pass

class TestExplainable(unittest.TestCase):

    def test_explainable(self):
        e = SomeExplainableThing()
        self.assertIsInstance(e.describe(), dict)
        self.assertIsInstance(e.explain(), dict)
