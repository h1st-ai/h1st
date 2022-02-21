from typing import Any

from h1st.core import GraphInfo
from h1st.core.engine import ExecutionEngine
from h1st.core.node import Node


class SimpleExecutionEngine(ExecutionEngine):

    def _linear_exec(self, node: Node, adj: dict, previous_output=None):
        next_nodes = adj[node]
        result = node.execute(previous_output)
        if next_nodes:
            return self._linear_exec(next_nodes[0], adj, result)
        return result

    def execute(self, graph: GraphInfo, data: Any):
        adj = graph.adjacency_list
        if not graph.is_linear:
            raise NotImplementedError("Executing non-linear graphs is not supported at the moment.")
        first_node = graph.root_nodes[0]
        result = self._linear_exec(first_node, adj, data)
        return result
