import os
import pandas as pd
from types import SimpleNamespace
from typing import Union, Optional, Callable, List, NoReturn, Any, Dict, Tuple

from .exception import GraphException
from .model import Model
from .node_containable import NodeContainable
from h1st.schema import SchemaValidator

class Node:
    """
    Base class for h1st Node
    """

    def __init__(self, containable: NodeContainable = None, id: str = None):
        """
        :param containable: instance of subclass of NodeContainable to attach to the node
        :param id: the node's id
        """
        if containable:
            containable._node = self
        
        self._id = id
        self._containable = containable
        self._graph = None
        self._edges = []        

        self._transform_input = None
        self._transform_output = None

        # viz attribute
        self.rank = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def edges(self) -> List[Tuple['Node', str]]:
        """
        :returns: list of tuple(next_node, edge_label) which next_node is connected from this node
            edge_label = 'yes'/'no' in case of condition nodes
            edge_label = None in case of normal nodes            
        """
        return self._edges

    @property
    def graph(self) -> 'Graph':
        return self._graph

    @graph.setter
    def graph(self, value):
        if self.graph:
            raise GraphException('This node belongs to another graph already')

        self._graph = value

    @property
    def transform_input(self) -> Callable:
        return self._transform_input

    @transform_input.setter
    def transform_input(self, value):
        """
        Transforms input of a node before executing the node

        .. code-block:: python
            :caption: Example of transform_input

            import h1st as hf

            class MyModel(h1.Model):
                pass

            class MyGraph(h1.Graph)
                def __init__(self):
                    self.start()
                        .add(MyModel(), id="my_model")
                        .end()

                    self.nodes.my_model.transform_input = self._transform_my_model_input

                def _transform_my_model_input(self, inputs):
                    inputs['xxx'] = ...
                    return inputs
        """
        self._transform_input = value

    @property
    def transform_output(self) -> Callable:
        return self._transform_output

    @transform_output.setter
    def transform_output(self, value):
        """
        Transforms output of a node after executing the node

        .. code-block:: python
            :caption: Example of transform_output

            import h1st as hf

            class MyModel(h1.Model):
                pass

            class MyGraph(h1.Graph)
                def __init__(self):
                    self.start()
                        .add(MyModel())
                        .end()

                    self.nodes.end.transform_output = self._transform_end_output

                def _transform_end_output(self, inputs):
                    return {
                        'result': inputs['xxx']
                    }
        """        
        self._transform_output = value

    def add(
        self,
        node: Union['Node', NodeContainable, None] = None,
        yes: Union['Node', NodeContainable, None] = None,
        no: Union['Node', NodeContainable, None] = None,
        id: str = None
     ) -> Union['Node', List['Node']]:
        """
        The bridge function to add nodes to a graph. This will invoke the Graph.add() function and 
        will then connect this node to newly added nodes.
        """
        return self._graph._add_and_connect(node, yes, no, id, self)

    def _execute(self, command: Optional[str], inputs: Dict[str, Any]) -> Dict:
        """
        The execution of graph will be executed recursively. The upstream node will invoke the down stream nodes to be executed.
        If it is the start node, this function will be invoked by the graph.
        The containable.call() will be invoked if this node contains a NodeContainable object. Otherwise, its call() function will be invoked.

        :param command: for this node to know which flow (predict, train, ...) the graph is running
        :param inputs: the input data to execute the node. During the graph execution, output of all executed nodes will be merged into inputs
        """
        if os.environ.get('DEBUG'):
            print('>>>', self.id, list(inputs))

        # transform input
        if callable(self.transform_input):
            transformed_inputs = self.transform_input(inputs)
            inputs.clear()
            inputs.update(transformed_inputs)

        # execute
        func = self._containable.call if self._containable else self.call        
        node_output = func(command, inputs)

        # transform output
        if self.id != "end" and callable(self.transform_output):
            if node_output:
                inputs.update(node_output)

            node_output = self.transform_output(inputs)

        # merge output
        if node_output:
            inputs.update(node_output)

        # recursively executing downstream nodes
        for edge in self.edges:
            edge_data = self._get_edge_data(edge, node_output)

            # data is available to execute the next node
            if edge_data is not None:
                next_node = edge[0]
                inputs.update(edge_data)

                next_output = next_node._execute(command, inputs)

                if next_output:
                    inputs.update(next_output)

        if self.id == 'end':
            return node_output
        else:
            output = {}

            if node_output:
                output.update(node_output)

            output.update(inputs)

            return output or inputs or {}

    def call(self, command: Optional[str], inputs: Dict[str, Any]) -> Dict:
        """
        Subclass may need to override this function to perform the execution depending the type of node.
        This function is invoked by the framework and user will never need to call it.
        """
        return {}

    def to_dot_node(self, visitor):
        """Subclass will need to implement this function to construct and return the graphviz compatible node"""
        pass

    def test_output(self, inputs: Any = None, schema=None, command='predict'):
        """
        Invokes the call function the node with given input data, then verifies if output of the node conforming with the output schema of this node.
        Framework will look up the output schema for this node in the schemas object loaded by the graph from schemas.py using id of this node.

        :param inputs: input data to invoke the call function of the node
        :param schema: provided schema to validate with output
        :param command: the command param to invoke the call function of the node
        """
        if self._containable:
            return self._containable.test_output(inputs, schema)
        else:
            output = self.call(command, inputs)
            return SchemaValidator().validate(output, schema)

    def _get_edge_data(self, edge, node_output):
        """Gets data from node's output to pass to the next node"""
        return node_output


class Action(Node):
    """
    @TODO: use .add(yes = (Model2(), "model2")) instead ?

    H1st non-conditional node. It is used to add a NodeContainable instance with an ID to yes/no branch of a conditional node

    .. code-block:: python
        :caption: Add nodes for yes/no branch of a conditional node

        import h1st as h1

        class MyGraph(h1.Graph)
            def __init__(self):
                yes, no = self.start()
                    .add(h1.Decision(Model1()))
                    .add(
                        yes = h1.Action(Model2(), id="model2"), # with an id
                        no = Model3()                           # without an id
                    )
                
                yes.add(Model4())
                no.add(Model5())

                self.end()
    """

    def to_dot_node(self, visitor):
        """Constructs and returns the graphviz compatible node"""
        return visitor.render_dot_action_node(self)


class Decision(Action):
    """
    H1st conditional node

    .. code-block:: python
        :caption: Graph with conditional node

        import h1st as h1

        class MyGraph(h1.Graph)
            def __init__(self):
                yes, no = self.start()
                    .add(h1.Decision(Model1()))
                    .add(
                        yes = Model2()
                        no = Model3()
                    )

                yes.add(Model4())
                no.add(Model5())
                
                self.end()
    """

    def __init__(self, containable: NodeContainable = None, id: str = None, result_field='results', decision_field='prediction'):
        """
        :param containable: instance of subclass of NodeContainable to attach to the node
        :param id: the node's id
        :param result_field: the key to extract the data collection from dictionary output of a conditional node
        :param decision_field: the field name to decide which item of the collection belongs to yes branch or no branch
        """
        super().__init__(containable, id)
        self._result_field = result_field
        self._decision_field = decision_field

    def call(self, command: Optional[str], inputs: Dict[str, Any]) -> Any:
        """
        This function is invoked by the framework and user will never need to call it.

        :returns:
            a dictionary containing 'results' key
                { 
                    'results': [{ 'prediction': True/False, ...}],
                    'other_key': ...,
                }

            or a dictionary containing only one key
                {
                    'your_key': [{ 'prediction': True/False, ...}]
                }
        """
        result = self._output
        
        if not isinstance(result, dict) or ((self._result_field not in  result) and len(list(result)) != 1):
            raise GraphException(f'output of {self._containable.__class__.__name__} must be a dict containing "results" field or only one key')
        
        return result    

    def to_dot_node(self, visitor):
        """Constructs and returns the graphviz compatible node"""
        return visitor.render_dot_decision_node(self)

    def _get_edge_data(self, edge, node_output):
        """splits data for yes/no path from the node's output to pass to the next node"""
        result_field = self._result_field if self._result_field in node_output else next(iter(node_output))
        results = node_output[result_field]

        decision_field = self._decision_field
        is_yes_edge = edge[1] == 'yes'

        if isinstance(results, pd.DataFrame):
            data = results[results[decision_field] == is_yes_edge]
        else:
            data = [item for item in results if item[decision_field] == is_yes_edge]

        return {result_field: data} if data is not None and len(data) > 0 else None
