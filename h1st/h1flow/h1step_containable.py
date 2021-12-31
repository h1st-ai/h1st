from typing import Dict
from h1st.exceptions.exception import GraphException
from h1st.trust.trustable import Trustable
# from h1st.schema.schema_validator import SchemaValidator
# from h1st.schema.schema_validation_result import SchemaValidationResult


class NodeContainable(Trustable):
    """
    Type of an instance to be added to a graph as a node must be the subclass of NodeContainable.
    .. code-block:: python
            :caption: Example of using NodeContainable

            import h1st.core as h1

            class GenerateWindowEvents(h1.NodeContainable):
                def call(self, command, inputs):
                    ...

            class MyGraph(h1.Graph):
                def __init__(self):
                    self
                        .start()
                        .add(GenerateWindowEvents())
                        .end()
        """
    def __init__(self):
        self._node = None
        
    @property
    def node(self) -> 'Node':
        if not self._node:
            from h1st.h1flow.h1flow import Graph 

            g = Graph()
            g.start()
            self._node = g.add(self)
            g.end()

        return self._node

    @property
    def graph(self) -> 'Graph':
        return self.node.graph

    def call(self, command: str, inputs: Dict) -> Dict:
        """
        Will be invoked by a node when executing a graph.

        Subclass of NodeContainable may override the call() function:
            import h1st.core as h1

            class MyClass(h1.NodeContainable)
                def call(self, command, inputs):
                    ...


        Or subclass may implement necessary functions which required for graph execution flows
        During executing, the function with name = value of command will be invoked
            class MyClass(h1.NodeContainable)                
                def predict(self, inputs):
                    # this function will be invoked if a graph execution is for predict:
                    # graph.predict(...)
                    # or graph.execute(command='predict', input_data=...)
                    ...
           
        :param command: to know which graph's execution flow (predict, train, ...) it is involving
        :inputs: input data to proceed accordingly to the flow

        :return: result as a dict
        """
        func = getattr(self, command)
        if not func:
            raise GraphException(f'class {self.__class__.__name__} must implement method "{command}')

        result = func(inputs)
        if not isinstance(result, dict):
            raise GraphException(f'output of {self.__class__.__name__} must be a dict')

        return result

    # def validate_node_output(self, input_data: dict=None, schema=None) -> SchemaValidationResult:
    #     """
    #     Subclass will implement this function to verify its output schema

    #     :param inputs: subclass will use this input data to call a specific function to get the result
    #     :schema: the schema to verify if the result conforming with
    #     """        
    #     return SchemaValidator().validate(input_data, schema)
