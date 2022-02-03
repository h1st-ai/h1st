from typing import Any

from h1st.core.node import Node


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

    def _validate_output(self, node_output) -> bool:
        """
        This will ensure the result's structure is valid for decision node.

        node_output must be a dictionary containing 'results' key and each item will have a field whose name = 'prediction'
        with bool value to decide whether the item belongs to yes or no branch
            {
                'results': [{ 'prediction': True/False, ...}],
                'other_key': ...,
            }
        or a dictionary containing only one key
            {
                'your_key': [{ 'prediction': True/False, ...}]
            }
        """
        if not isinstance(node_output, dict) or (
                (self._result_field not in node_output) and len(node_output.keys()) != 1):
            raise GraphException(
                f'output of {type(self._containable)} must be a dict containing "results" field or only one key')

        return True

    def execute(self, *previous_output: Any):
        node_output = self._node.execute(previous_output)
        self._validate_output(node_output)

