from random import random
from typing import Any

import pytest

from h1st.core.graph import Graph
from h1st.core.node import Node


class SomeNode(Node):

    def execute(self, *previous_output: Any):
        print("hello")


class DataNode(Node):

    def execute(self, *previous_output: Any):
        return [random(), random(), random()]


class TestUpdatedGraph:

    def test_add_node(self):
        g = Graph()
        data_node1 = DataNode()
        g.add_node(data_node1)
        assert len(g.get_info().nodes) == 1

    def test_invalid_node_type(self):
        with pytest.raises(TypeError):
            g = Graph()
            g.add_node("SomeNode")

    def test_add_edge(self):
        g = Graph()
        data_node1 = DataNode()
        data_node2 = DataNode()
        g.add_edge(data_node1, data_node2)
        graph_info = g.get_info()
        assert len(graph_info.nodes) == 2
        assert len(graph_info.edges) == 1
        assert len(graph_info.root_nodes) == 1
        assert graph_info.adjacency_list[data_node1] == [data_node2]

    def test_is_linear(self):
        g = Graph()
        data_node1 = DataNode()
        data_node2 = DataNode()
        g.add_node(data_node1)
        g.add_node(data_node2)
        g.add_edge(data_node1, data_node2)
        assert g.get_info().is_linear
        data_node3 = DataNode()
        g.add_node(data_node3)
        g.add_edge(data_node1, data_node3)
        assert len(g.get_info().root_nodes) == 1
        assert not g.get_info().is_linear

    def test_add_sequential(self):
        """
        data_node -> some_node
        """
        g = Graph()
        data_node = DataNode()
        some_node = DataNode()
        g.add(data_node)
        g.add(some_node)
        graph_info = g.get_info()
        assert len(graph_info.root_nodes) == 1
        assert graph_info.is_linear
        assert len(graph_info.nodes) == 2
        assert graph_info.adjacency_list[data_node] == [some_node]
        assert graph_info.adjacency_list[some_node] == []

    def test_add_converging(self):
        """
        data_node1 -> some_node
        data_node2 -> some_node
        """
        graph = Graph()
        data_node1 = DataNode()
        data_node2 = DataNode()
        some_node = SomeNode()
        graph.add(some_node, previous_nodes=[data_node1, data_node2])
        graph_info = graph.get_info()
        assert len(graph_info.root_nodes) == 2
        assert not graph_info.is_linear
        assert len(graph_info.nodes) == 3
        assert graph_info.adjacency_list[data_node1] == [some_node]
        assert graph_info.adjacency_list[data_node2] == [some_node]

    def test_add_diverging(self):
        """
        some_node -> data_node1
        some_node -> data_node2
        """
        graph = Graph()
        data_node1 = DataNode()
        data_node2 = DataNode()
        some_node = SomeNode()
        graph.add(data_node1, previous_nodes=[some_node])
        graph.add(data_node2, previous_nodes=[some_node])
        graph_info = graph.get_info()
        assert len(graph_info.root_nodes) == 1
        assert not graph_info.is_linear
        assert len(graph_info.nodes) == 3
        assert graph_info.adjacency_list[some_node] == [data_node1, data_node2]
