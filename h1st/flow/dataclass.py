from dataclasses import dataclass

from h1st.core.node import Node
from h1st.flow.graph import Graph


@dataclass
class GraphNode:
    node: Node
    graph: Graph

    def add(self,
            node: Node = None,
            yes: Node = None,
            no: Node = None
            ):
        return self.graph.add(node, yes, no, [self.node])
