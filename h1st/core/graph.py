import collections

from h1st.core import NodeInfo, GraphInfo
from h1st.core.execution import ExecutionManager
from h1st.core.node import Node


class Graph:
    def __init__(self) -> None:
        self.__graph = {}  # dictionary of Node -> NodeInfo
        self.__root_nodes: list[Node] = []
        self.__non_root_nodes: list[Node] = []
        self.__last_updated_node: Node = None

    def add_node(self, node: Node):
        if not isinstance(node, Node):
            raise TypeError("must be Node, not {}".format(type(node).__name__))
        if node not in self.__graph.keys():
            self.__graph[node] = NodeInfo()
            self.__last_updated_node = node

    def add_edge(self, from_node: Node, to_node: Node):
        if not isinstance(from_node, Node):
            raise TypeError("must be Node, not {}".format(type(from_node).__name__))
        if not isinstance(to_node, Node):
            raise TypeError("must be Node, not {}".format(type(to_node).__name__))
        is_root_node = to_node in self.__root_nodes
        if is_root_node and len(self.__root_nodes) == 1:
            raise RuntimeError("There must be one or more root nodes")
        if from_node not in self.__graph.keys():
            self.add_node(from_node)
        if to_node not in self.__graph.keys():
            self.add_node(to_node)
        if from_node in self.__graph[to_node].next_nodes:
            raise RuntimeError("Cannot add edge as it results in a closed loop")
        if to_node not in self.__graph[from_node].next_nodes and \
                from_node not in self.__graph[to_node].next_nodes:
            self.__graph[from_node].next_nodes.append(to_node)
            self.__graph[to_node].has_previous = True
            self.__non_root_nodes.append(to_node)
            self.__last_updated_node = to_node
            if from_node not in self.__non_root_nodes and from_node not in self.__root_nodes:
                self.__root_nodes.append(from_node)
            if is_root_node:
                self.__root_nodes.remove(to_node)

    def show(self):
        # TODO port visualization
        print(self.__graph)

    def get_info(self):
        nodes = list(self.__graph.keys())
        edges = list()
        adjacency_list = {}
        is_linear = True
        all_next_nodes = list()
        for node in self.__graph.keys():
            next_nodes = self.__graph[node].next_nodes
            adjacency_list[node] = next_nodes
            if len(next_nodes) > 1:
                is_linear = False
            for next_node in next_nodes:
                edges.append((node, next_node))
                all_next_nodes.append(next_node)
        group_by_occurrence = collections.Counter(all_next_nodes)
        filtered = filter(lambda elem_count: elem_count > 1, group_by_occurrence.values())
        is_linear = is_linear and len(list(filtered)) == 0
        return GraphInfo(nodes, edges, adjacency_list, self.__root_nodes, is_linear)

    def execute(self):
        graph_info = self.get_info()
        return ExecutionManager.execute_with_engine(graph_info)

    def add(self, node: Node, after: list[Node] = None):
        if after is None:
            if self.__last_updated_node is None:
                self.add_node(node)
            else:
                self.add_edge(self.__last_updated_node, node)
        else:
            for from_node in after:
                self.add_edge(from_node, node)
        self.__last_updated_node = node
