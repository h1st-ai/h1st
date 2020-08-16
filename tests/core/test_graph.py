import math
from unittest import TestCase, skip
from h1st.core import NodeContainable
import h1st as h1

class GraphTestCase(TestCase):
    def test_execution(self):
        '''
        to ensure the graph works well with mix of Model and Action nodes as well as transform_input/output
        
        '''

        class MyModel(h1.Model):
            def predict(self, inputs):
                values = inputs['values']
                filtered = list(filter(lambda i: i['x'] >= 2, values))

                return { 'model_result': filtered }

        class MyAction(h1.NodeContainable):
            def call(self, command, inputs):
                values = inputs['model_result'][:10]

                for i in range(len(values), 10):
                    values.append({ 'x': 0 })

                return { 'ensure_output': values }
                
        class MyGraph(h1.Graph):
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
                values = [ { 'x': math.floor(i['x'])} for i in values]
                return { 'values': values }

            def transform_end_output(self, inputs):
                values = inputs['ensure_output']
                total = sum([i['x'] for i in values])

                return {
                    'total': total,
                    'arr': values
                }
        
        g = MyGraph()

        values = [
            { 'x': 1.5 },
            { 'x': 2.5 },
            { 'x': 4.5 },
        ]

        result = g.execute(
            command='predict',
            data={'values': values})

        self.assertEqual(len(result['arr']), 10)
        self.assertEqual(result['total'], sum([math.floor(i['x']) for i in values if math.floor(i['x']) >= 2]))
