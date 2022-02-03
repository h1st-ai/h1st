import sys
from types import SimpleNamespace
from typing import List, Union, Any, NoReturn, Dict

from h1st.core.graph import Graph as CoreGraph
from h1st.core.node import Node
from h1st.flow import GraphNode


class Graph:
    """
    A Graph is itself a NodeContainable, meaning it can be enclosed within a Node,
    forming a hierarchy of Graphs

    ```mermaid
    graph TD
    A[Hard] -->|Text| B(Round)
    B --> C{Decision}
    C -->|One| D[Result 1]
    C -->|Two| E[Result 2]

    """

    def __init__(self):
        self.__internal_graph: CoreGraph = CoreGraph()
        self._last_added_node = None

    @property
    def nodes(self) -> list[Node]:
        """
        Gets all nodes of the graph in unspecified orders
        TODO Gets a specific node by ID: nodes.<ID>
        """
        return self.__internal_graph.get_info().nodes

    def add(self,
            node: Node = None,
            yes: Node = None,
            no: Node = None,
            after: list[Node] = None
            ) -> Union[GraphNode, List[GraphNode]]:
        """
        Adds a new Node or NodeContainable to this graph. Period keeps a running preference to the current position
        in the graph to be added If the object to be added is a NodeContainable then a new node will be automatically
        instantiated to contain that object and the node is added to this graph. The new node's id can be specified
        or automatically inferred from the NodeContainable's type.

        :param node: Node or NodeContainable object to be added to the graph
        :param yes/no: Node or NodeContable object to be added to the graph following a conditional (Decision) node
        :param after: the nodes to which the new node will be connected

        :return:
            new added node if adding a single node
            Or new added node for yes branch if adding yes node only (without no node) following a condition node
            Or new added node for no branch if adding no node only (without yes node) following a condition node
            Or [new added node for yes branch, new added node for no branch] if adding both yes & no nodes following a condition node

        .. code-block:: python
            :caption: Cyber Security example to handle injection and replacement attacks

            import h1st.core as h1
            from h1st.core import NodeContainable, Decision

            class MyGraph(h1.Graph):
                def __init__(self):
                    super().__init__()

                    imc, rec = self
                        .start()
                        .add(GenerateWindowEvents())
                        .add(Decision(InjectionEventClassifier()))
                        .add(
                            yes=InjectionMessageClassifier(),
                            no=Decision(ReplacementEventClassifier())
                        )

                    rec.add(
                        yes=ReplacementMessageClassifier(),
                        no=BuildNormalResult()
                    )

                    self.end()

        """
        self.__internal_graph.add(node)
        # n = GraphNode(node, graph=self)
        if yes is not None:
            self.__internal_graph.add(yes)
        if no is not None:
            self.__internal_graph.add(no, after=[node])

    def execute(self, data: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
        """
        The graph will scan through nodes to invoke appropriate node's function with name = value of command
        parameter. Everytime the graph invokes the appropriate function of the node, it will passing an accumulated
        dictionary as the input and merge result of the function into the accumulated dictionary.

        :param command: for Node or NodeContainable object to decide which function will be invoked during executing the graph
        :param data: input data to execute.
            if data is a dictionary, the graph will execute one.
            if data is a list of dictionary, the graph will execute multiple time

        :return:
            single dictionary if the input is a single dictionary
            Or list of dictionary if the input is a list of dictionary

        .. code-block:: python
            :caption: Example graph for Cyber Security and how to execute the graph

            import h1st.core as h1
            from h1st.core import NodeContainable, Decision

            class MyGraph(h1.Graph):
                def __init__(self):
                    imc, rec = self
                        .start()
                        .add(GenerateWindowEvents())
                        .add(Decision(InjectionEventClassifier()))
                        .add(
                            yes=InjectionMessageClassifier(),
                            no=Decision(ReplacementEventClassifier())
                        )

                    rec.add(
                        yes=ReplacementMessageClassifier(),
                        no=BuildNormalResult()
                    )

                    self.end()

            g = MyGraph()
            result = g.execute(command='predict', data={'df': my_dataframe})
        """
        if isinstance(data, list):
            return [self.__internal_graph.execute(item) for item in data]

        return self.__internal_graph.execute(data)

    def visualize(self):
        """Visualizes the flowchart for this graph"""
        return self.__internal_graph.show()

