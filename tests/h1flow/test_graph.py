import math
from unittest import TestCase, skip
from h1st.h1flow.h1flow import Graph
from h1st.h1flow.h1step import NodeContainable, Decision
from h1st.model.model import Model


class GraphTestCase(TestCase):
    def test_execution(self):
        """
        to ensure the graph works well with mix of Model and Action nodes as well as transform_input/output

        """

        class MyModel(Model):
            def predict(self, inputs):
                values = inputs['values']
                filtered = list(filter(lambda i: i['x'] >= 2, values))

                return {'model_result': filtered}

        class MyAction(NodeContainable):
            def call(self, command, inputs):
                values = inputs['model_result'][:10]

                for i in range(len(values), 10):
                    values.append({'x': 0})

                return {'ensure_output': values}

        class MyGraph(Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(MyModel())
                        .add(MyAction())
                )

                self.end()

                self.nodes.start.transform_input = self.transform_start_input
                self.nodes.end.transform_output = self.transform_end_output

            def transform_start_input(self, inputs):
                values = inputs['values']
                values = [{'x': math.floor(i['x'])} for i in values]
                return {'values': values}

            def transform_end_output(self, inputs):
                values = inputs['ensure_output']
                total = sum([i['x'] for i in values])

                return {
                    'total': total,
                    'arr': values
                }

        g = MyGraph()

        input_values = [
            {'x': 1.5},
            {'x': 2.5},
            {'x': 4.5},
        ]

        result = g.execute(
            command='predict',
            data={'values': input_values})

        self.assertEqual(len(result['arr']), 10)
        self.assertEqual(result['total'], sum([math.floor(i['x']) for i in input_values if math.floor(i['x']) >= 2]))

    def test_override_output_key(self):
        arr = [
            {'x': 100, 'prediction': True},
            {'x': 200, 'prediction': False},
            {'x': 300, 'prediction': True},
            {'x': 400, 'prediction': True},
        ]

        class MyModel(Model):
            def predict(self, inputs):
                return {
                    "results": arr
                }

        class YesAction(NodeContainable):
            def call(self, command, inputs):
                return {'results': sum([i['x'] for i in inputs['results']])}

        class NoAction(NodeContainable):
            def call(self, command, inputs):
                return {'no_results': sum([i['x'] for i in inputs['results']])}

        class MyGraph(Graph):
            def __init__(self):
                super().__init__()

                yes_node, no_node = (
                    self.start()
                    .add(Decision(MyModel()))
                    .add(
                        yes=YesAction(),
                        no=NoAction()
                    )
                )

                self.end()

                self.nodes.end.transform_output = lambda inputs: {
                    'result': inputs['results'] + inputs['no_results'] * 1000}

        result = MyGraph().predict(data={})

        expected_result = sum([i['x'] for i in arr if i['prediction']]) + sum(
            [i['x'] for i in arr if not i['prediction']]) * 1000
        self.assertEqual(result['result'], expected_result)
