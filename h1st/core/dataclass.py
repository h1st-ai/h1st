from dataclasses import dataclass, field
from typing import Tuple

from h1st.core.node import Node


@dataclass
class GraphInfo:
    nodes: list[Node]
    edges: list[Tuple[Node, Node]]
    adjacency_list: dict
    root_nodes: list[Node]
    is_linear: bool


@dataclass
class NodeInfo:
    next_nodes: list[Node] = field(default_factory=list)
    has_previous: bool = False
    visual_attributes: dict = field(default_factory=dict)
