import sys
from types import SimpleNamespace
from typing import List, Union, Any, NoReturn, Dict

from .h1step import Node, Action
from .h1step_containable import NodeContainable
from h1st.exceptions.exception import GraphException
from h1st.core.viz import DotGraphVisualizer
from h1st.trust.trustable import Trustable


# __TODO__: refactor to Flows and Steps

class Graph(NodeContainable, Trustable):
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

    def __init__(self, node_validation_schema_name='NODE_VALIDATION_SCHEMA'):
        """
        :param node_validation_schema_name: name of the variable in config.py to load schema definition fornode_validation_schema_name
        """
        super().__init__()
        self._node_validation_schema = None
        self._node_validation_schema_name = node_validation_schema_name

        self._nodes = SimpleNamespace()
        self._last_added_node = None

        # map { node's id: number} to trake the used ids.
        # with number=0 if id is manual provided, number=1 if id is generated
        self._used_node_ids = {} 

    @property
    def nodes(self) -> SimpleNamespace:
        """
        Gets all nodes of the graph in unspecified orders
        Gets a specific node by ID: nodes.<ID>
        """
        return self._nodes

    def start(self) -> 'Graph':
        """
        Initial action to begin adding nodes to a (fresh) Graph. A node with the id='start' will be
        automatically added to the Graph.
        """
        return self.add(Action(id='start'))

    def add( self,
        node: Union[Node, NodeContainable, None] = None,
        yes: Union[Node, NodeContainable, None] = None,
        no: Union[Node, NodeContainable, None] = None,
        id: str = None
     ) -> Union[Node, List[Node]]:        
        """
        Adds a new Node or NodeContainable to this graph. Period keeps a running preference to the current possition in the graph to be added
        If the object to be added is a NodeContainable then a new node will be automatically instanciated to contain that object and the node is added to this graph.
        The new node's id can be specified or automatically inferred from the NodeContainable's type.

        :param node: Node or NodeContainable object to be added to the graph
        :param yes/no: Node or NodeContable object to be added to the graph following a conditional (Decision) node
        :param from_: the node to which the new node will be connected
        :param id: the id of the new node

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
        return self._add_and_connect(node, yes, no, id, self._last_added_node)

    def end(self) -> 'Graph':
        """
        This method is required after adding all nodes to the graph. The end node with id='end' will be automatically added to the graph.
        All leaf nodes (without outgoing edges) will be automatically connected to the end node.
        Consolidate ids for nodes using the same NodeContainable type without provided id. Ids will be Xyz1, Xyz2, ... with class Xyz inherits from NodeContainable
        """
        end_node = self.add(Action(id='end'))

        # connect all nodes without out-going edges to end node
        for id, node in self.nodes.__dict__.items():
            if not node.edges and id != end_node.id:
                self._connect_nodes(node, end_node)

        return end_node

    def execute(self, command: str, data: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
        """
        The graph will scan through nodes to invoke appropriate node's function with name = value of command parameter.
        Everytime the graph invokes the appropreate function of the node, it will passing an accumulated dictionary as the input and merge result of the function into the accumulated dictionary.

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
            return [self._execute_one(command, item) for item in data]

        return self._execute_one(command, data)

    def predict(self, data) -> Any:
        """ A shortcut function for the "execute" function with command="predict" """
        return self.execute('predict', data)

    def visualize(self):
        """Visualizes the flowchart for this graph"""
        vs = DotGraphVisualizer(self)
        return vs

    def describe(self):
        pass

    def explain(self):
        pass

    def _wrap_and_add(self, node: Union[Node, NodeContainable], id: str = None):
        """
        Wraps NodeContainable to a Node if needed. Override node's id if an id provided. Then adds the node to the graph.

        :param node: a Node or ContainableNode
        :param id: id for the node

        :return: the newly added node
        """
        if not isinstance(node, (Node, NodeContainable)):
            raise GraphException('object to add to a graph must be an instance of Node or NodeContainable')

        if isinstance(node, NodeContainable):
            containable = node
            node = Action(containable)

        id = id or node.id
        if id: # manual provided id
            self._used_node_ids[id] = 0
        else: # automatic id
            id = self._generate_id(node)
            self._used_node_ids[id] = 1 

        node._id = id
        node.graph = self
        setattr(self.nodes, id, node)

        return node

    def _generate_id(self, node: Node):
        """
        Automatically generates an id for the node.
        If multiple instances of the same NodeContainable type are added,
        the ids of the node will be ClassName, ClassName2, ClassName3, etc
        """
        classname = (node._containable or node).__class__.__name__.split('.')[-1]

        if classname not in self._used_node_ids:
            return classname

        for i in range(2, sys.maxsize):
            id = f'{classname}{i}'
            if id not in self._used_node_ids:
                return id

    def _connect_nodes(self, from_: Node, to: Node, edge_label=None) -> NoReturn:
        """
        Connects "from_" node to the "to" node

        :param from_: the source node
        :param to: the destination node
        :edge_label: the label for the edge between from_ and to
        """
        if not from_:
            return

        if edge_label not in ['yes', 'no', None]:
            raise GraphException(
                f'edge_label="{edge_label}" is not supported')

        from_.edges.append(
            (to, edge_label)
        )

    def _execute_one(self, command: str, data: Dict) -> Dict:
        """
        Executes the graph exactly 1 time

        :param command: for Node or NodeContainable object to decide which function will be invoked during executing the graph
        :param data: input data to execute the graph

        :return: result as a dictionary
        """
        output = self.nodes.start._execute(command, data, {})

        if self.nodes.end.transform_output:
            output = self.nodes.end.transform_output(output)

        return output

    def _add_and_connect( self,
        node: Union[Node, NodeContainable, None] = None,
        yes: Union[Node, NodeContainable, None] = None,
        no: Union[Node, NodeContainable, None] = None,        
        id: str = None,
        from_: Union[Node, None] = None
     ) -> Union[Node, List[Node]]:
        """
        Adds node/yes/no nodes to self.nodes and connect from_node to newly added nodes
        """
        if id == 'start' and hasattr(self.nodes, 'start'):
            raise GraphException('Graph.start() may only be called once')

        if id == 'end' and hasattr(self.nodes, 'end'):
            raise GraphException('Graph.end() may only be called once')        

        if hasattr(self.nodes, 'end'):
            raise GraphException('not allow to add a node after Graph.end()')

        if id and hasattr(self.nodes, id):
            raise GraphException(f'Node id={id} is duplicated')

        # connect to latest node if not adding from a node
        if not from_:
            from_ = self._last_added_node

        # add a single node
        if node:
            node = self._wrap_and_add(node, id)
            self._connect_nodes(from_, node)

            # keep reference to the latest node
            self._last_added_node = node

            return node

        # add nodes with edge_label 'yes' / 'no'
        return_nodes = []

        if yes:
            node = self._wrap_and_add(yes)
            self._connect_nodes(from_, node, 'yes')
            return_nodes.append(node)

        if no:
            node = self._wrap_and_add(no)
            self._connect_nodes(from_, node, 'no')
            return_nodes.append(node)

        # keep reference to the latest node
        self._last_added_node = return_nodes[0] if len(return_nodes) == 1 else None

        # chaining will return array if having more than one node, otherwise return single node
        return return_nodes[0] if len(return_nodes) == 1 else return_nodes
