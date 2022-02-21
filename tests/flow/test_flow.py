from typing import Any

import pytest

from h1st.nodes.decision import Decision
from h1st.nodes.filter_key import FilterByKey
from tests.flow.nodes.test_decision import DummyModel
from tests.test_fixture import mock_env_simple

from h1st.core.node import Node
from h1st.flow.graph import Graph


class ListStats(Node):

    def execute(self, previous_output: Any = None):
        result = {}
        if isinstance(previous_output, list):
            total = sum(previous_output)
            result = {'sum': total, 'avg': total / len(previous_output)}
        return result


@pytest.mark.usefixtures("mock_env_simple")
class TestGraphWrapper:
    def test_execution_with_yes(self):
        flow_graph = Graph()
        yes_node = flow_graph.add(Decision(DummyModel()), yes=FilterByKey("value"))
        yes_node.add(ListStats())
        result = flow_graph.execute([10, 15, 16, 20])
        assert result is not None
        assert isinstance(result, dict)
        assert result["sum"] == 61
        assert result["avg"] == 15.25
