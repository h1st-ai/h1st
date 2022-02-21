from typing import Any, Final

from h1st.core.node import Node

YES_RESULT_FIELD: Final = "yes_result"
NO_RESULT_FIELD: Final = "no_result"


class Decision(Node):
    """
    H1st conditional node
    .. code-block:: python
        :caption: Graph with conditional node
        import h1st.core as h1
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
    .. code-block:: python
        :caption: Graph with conditional node using custom result_field and decision_field
        import h1st.core as h1
        class Model1(h1.Model):
            def predict(data):
                return {
                    'predictions': [
                        {gx: 10, gy: 20, label: True},
                        {gx: 11, gy: 21, label: True},
                        {gx: 12, gy: 22, label: False},
                    ]
                }
        class MyGraph(h1.Graph)
            def __init__(self):
                yes, no = self.start()
                    .add(h1.Decision(Model1(), result_field='predictions', decision_field='label'))
                    .add(
                        yes = Model2()
                        no = Model3()
                    )
                yes.add(Model4())
                no.add(Model5())

                self.end()
    """

    def __init__(self, node: Node, result_field='results', decision_field='prediction'):
        """
        :param node: instance of subclass of Node
        :param result_field: the key to extract the data collection from dictionary output of a conditional node
        :param decision_field: the field name to decide which item of the collection belongs to yes branch or no branch
        """
        self._node = node
        self._result_field = result_field
        self._decision_field = decision_field

    def to_dot_node(self, visitor):
        """Constructs and returns the graphviz compatible node"""
        return visitor.render_dot_decision_node(self)

    def execute(self, previous_output: Any):
        """splits data for yes/no path from the node's output to pass to the next node"""
        node_output = self._node.execute(previous_output)
        result_field = self._result_field if self._result_field in node_output else next(iter(node_output))
        results = node_output[result_field]

        decision_field = self._decision_field
        yes_result, no_result = [], []
        for x in results:
            (no_result, yes_result)[x[decision_field]].append(x)
        decision_results = {YES_RESULT_FIELD: yes_result, NO_RESULT_FIELD: no_result}
        return decision_results
