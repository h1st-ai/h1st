import abc

from h1st.core.graph import GraphInfo
from h1st.core.node import Node


class ExecutionEngine(abc.ABC):
    @abc.abstractmethod
    def execute(self, graph: GraphInfo):
        pass


class SimpleExecutionEngine(ExecutionEngine):

    def _linear_exec(self, node: Node, adj: dict, previous_output=None):
        if previous_output is None:
            previous_output = {}
        next_nodes = adj[node]
        result = node.execute(previous_output)
        if next_nodes:
            return self._linear_exec(next_nodes[0], adj, result)
        return result

    def execute(self, graph: GraphInfo):
        adj = graph.adjacency_list
        if not graph.is_linear:
            raise NotImplementedError("Executing non-linear graphs is not supported at the moment.")
        first_node = graph.root_nodes.pop()
        result = self._linear_exec(first_node, adj)
        return result
