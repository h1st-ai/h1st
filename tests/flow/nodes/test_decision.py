from typing import Any

from h1st.core.node import Node
from h1st.nodes.decision import Decision


class DummyModel(Node):

    def execute(self, previous_output: Any):
        return {
            "results": [
                {'value': value, 'prediction': value >= 10} for value in previous_output
            ]
        }


class TestDecisionNode:
    def test_decision_yes_no(self):
        yes_result, no_result = Decision(DummyModel()).execute([10, 5, 6, 20])
        assert len(yes_result) == 2
        assert len(no_result) == 2
        assert list(map(lambda x: x['value'], yes_result)) == [10, 20]
        assert list(map(lambda x: x['value'], no_result)) == [5, 6]
