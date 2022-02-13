from typing import Any

import pytest
from tests.test_fixture import mock_env_simple

from h1st.core.graph import Graph
from h1st.core.node import Node


class DataNode(Node):
    def execute(self, previous_output: Any):
        return [3, 11, 37, 101]


class TransformNode(Node):
    def execute(self, previous_output: Any):
        result = []
        if isinstance(previous_output, list):
            result = list(map(lambda x: x + 10, previous_output))
        return result


@pytest.mark.usefixtures("mock_env_simple")
class TestSimpleExecutionEngine:
    def test_execution(self):
        g = Graph()
        data_gen = DataNode()
        transform = TransformNode()
        g.add_edge(data_gen, transform)
        result = g.execute()
        assert len(result) == 4
        assert result == [13, 21, 47, 111]
