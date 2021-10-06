import os
from typing import Any

from h1st.core.graph import Graph
from h1st.core.node import Node


class DataNode(Node):
    def execute(self, *previous_output: Any):
        return [3, 11, 37, 101]


class TransformNode(Node):
    def execute(self, *previous_output: Any):
        result = []
        for out in previous_output:
            if isinstance(out, list):
                result = list(map(lambda x: x + 10, out))
        return result


class TestSimpleExecutionEngine:
    def test_execution(self):
        os.environ["H1ST_ENGINE"] = "h1st.core.engine.SimpleExecutionEngine"
        g = Graph()
        data_gen = DataNode()
        transform = TransformNode()
        g.add_edge(data_gen, transform)
        result = g.execute()
        assert result == [13, 21, 47, 111]
