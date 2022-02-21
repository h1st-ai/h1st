from typing import Any

from h1st.core.node import Node
from h1st.nodes.decision import Decision, YES_RESULT_FIELD, NO_RESULT_FIELD


class DummyModel(Node):

    def execute(self, previous_output: Any):
        return {
            "results": [
                {'value': value, 'prediction': value >= 10} for value in previous_output
            ]
        }


class TestDecisionNode:
    def test_decision_yes_no(self):
        result = Decision(DummyModel()).execute([10, 5, 6, 20])
        yes_result = result[YES_RESULT_FIELD]
        no_result = result[NO_RESULT_FIELD]
        assert len(yes_result) == 2
        assert len(no_result) == 2
        assert list(map(lambda x: x['value'], yes_result)) == [10, 20]
        assert list(map(lambda x: x['value'], no_result)) == [5, 6]
