import pandas as pd
from unittest import TestCase, skip
from h1st.core import Graph, Decision, Action, NodeContainable, GraphException
import h1st as h1


class DummyAction(h1.NodeContainable):
    def call(self, command, inputs):
        return {}

class DummyModel(h1.Model):
    def call(self, command, inputs):
        return {}

class NodeIdTestCase(TestCase):
    def test_non_duplicated_node_ids(self):
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(DummyAction())                        
                )

                self.end()

        g = MyGraph()
        self.assertNotEqual(g.nodes.DummyAction, None) 

    def test_multiple_nodes_same_class_without_node_id(self):
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(DummyAction())
                        .add(DummyAction())
                        .add(DummyAction())                        
                )

                self.end()

        g = MyGraph()
        result = g.execute(command='predict', data={})

        self.assertEqual(result, {})
        self.assertNotEqual(g.nodes.DummyAction, None)
        self.assertNotEqual(g.nodes.DummyAction2, None)
        self.assertNotEqual(g.nodes.DummyAction3, None)

    def test_duplicated_node_ids(self):
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(DummyAction(), id='node1')
                        .add(DummyAction())
                        .add(DummyAction(), id='node1')                        
                )

                self.end()

        self.assertRaises(GraphException, lambda: MyGraph())  

class ActionNodeTestCase(TestCase):
    def setUp(self):
        class Action1(h1.NodeContainable):
            def call(self, command, inputs):
                return {
                    'aaa': inputs['a'],
                    'sum1': 10
                }

        class Action2(h1.NodeContainable):
            def call(self, command, inputs):
                return {
                    'bbb': inputs['b'],
                    'sum2': inputs['sum1'] + 100
                }

        class Action3(h1.NodeContainable):
            def call(self, command, inputs):
                return {
                    'ccc': inputs['c'],
                    'sum3': inputs['sum2'] + 1000
                }

        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(Action1())
                        .add(Action2())
                        .add(Action3())                        
                )

                self.end()
        
        self._g = MyGraph()

    def test_action_call(self):
        result = self._g.predict(data={ 'a': 5, 'b': 10, 'c': 15 })
        self.assertEqual(result['sum3'], 1110)
        self.assertEqual(result['aaa'], 5)
        self.assertEqual(result['bbb'], 10)
        self.assertEqual(result['ccc'], 15)

class SimpleDecisionNodeTestCase(TestCase):
    def _create_and_excute_graph_with_decision_node(self, input_data):
        '''
        Test script:
            given input as array of value, decision will split value >= 10 to yes/no branches
            then each downstream node will calculate its sum
        '''

        class MyModel(h1.Model):
            def predict(self, inputs):
                return {
                    "results": [
                        {'value': value, 'prediction': value >=10 } for value in inputs['values']
                    ]
                }

        class YesAction(h1.NodeContainable):
            def call(self, command, inputs):
                return {'yes_sum': sum(i['value'] for i in inputs['results'])}

        class NoAction(h1.NodeContainable):
            def call(self, command, inputs):
                return {'no_sum': sum(i['value'] for i in inputs['results'])}                
                
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                yes_node, no_node = (
                    self
                        .start()
                        .add(DummyAction())
                        .add(Decision(MyModel()))
                        .add(
                            yes = YesAction(),
                            no = NoAction()
                        )
                )

                no_node.add(DummyAction())
                self.end()  
        
        g = MyGraph()
        return g.predict(data={'values': input_data})

    def test_decision_yes_no(self):
        result = self._create_and_excute_graph_with_decision_node([10, 5, 6, 20])
        self.assertEqual(result['yes_sum'], 30)
        self.assertEqual(result['no_sum'], 11)

    def test_decision_yes_only(self):
        result = self._create_and_excute_graph_with_decision_node([10, 15, 16, 20])
        self.assertEqual(result['yes_sum'], 61)

    def test_decision_no_only(self):
        result = self._create_and_excute_graph_with_decision_node([1, 2, 3, 4])
        self.assertEqual(result['no_sum'], 10)

    def test_decision_node_returning_dataframe(self):
        x = [1, 2, 3, 4]
        y = [5, 10, 15, 20]
        predictions = [True, False, False, True]

        class MyModel(h1.Model):
            def predict(self, inputs):
                return {
                    "results": pd.DataFrame({
                            'x': x,
                            'y': y,
                            'label': predictions
                        })
                }

        class YesAction(h1.NodeContainable):
            def call(self, command, inputs):
                df = inputs['results']
                return {'yes_sum': sum(df['x']*df['y'])}

        class NoAction(h1.NodeContainable):
            def call(self, command, inputs):
                df = inputs['results']
                return {'no_sum': sum(df['x']*df['y'])}
                
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                yes_node, no_node = (
                    self
                        .start()
                        .add(DummyAction())
                        .add(Decision(MyModel(), decision_field='label'))
                        .add(
                            yes = YesAction(),
                            no = NoAction()
                        )
                )

                no_node.add(DummyAction())
                self.end() 
                        
        result = MyGraph().predict(data={})

        expected_yes_sum = sum([x[i]*y[i] for i in range(len(x)) if predictions[i]])
        self.assertEqual(result['yes_sum'], expected_yes_sum)

        expected_no_sum = sum([x[i]*y[i] for i in range(len(x)) if not predictions[i]])
        self.assertEqual(result['no_sum'],  expected_no_sum)

    def test_decision_node_with_transform_output_for_yes_no_branches(self):
        x = [10, 100, 1000, 10000]
        predictions = [False, False, True, False]

        class MyModel(h1.Model):
            def predict(self, inputs):
                return {
                    "results": pd.DataFrame({
                            'x': x,
                            'prediction': predictions
                        })
                }

        class YesAction(h1.NodeContainable):
            def call(self, command, inputs):
                df = inputs['results']
                return {'results': sum(df['x'])}

        class NoAction(h1.NodeContainable):
            def call(self, command, inputs):
                df = inputs['results']
                return {'results': sum(df['x'])}
                
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                yes_node, no_node = (
                    self
                        .start()
                        .add(DummyAction())
                        .add(Decision(MyModel()))
                        .add(
                            yes = YesAction(),
                            no = NoAction()
                        )
                )

                no_node.add(DummyAction())                
                self.end() 

                self.nodes.YesAction.transform_output = lambda inputs: {'yes_sum': inputs['results']}
                self.nodes.NoAction.transform_output = lambda inputs: {'no_sum': inputs['results']}
                        
        result = MyGraph().predict(data={})

        expected_yes_sum = sum([x[i] for i in range(len(x)) if predictions[i]])
        self.assertEqual(result['yes_sum'], expected_yes_sum)

        expected_no_sum = sum([x[i] for i in range(len(x)) if not predictions[i]])
        self.assertEqual(result['no_sum'],  expected_no_sum)

class ModelNodeTestCase(TestCase):
    def test_model_predict(self):
        class Model1(h1.Model):
            def predict(self, inputs):
                return {
                    'model1_input': inputs['model1'],
                    'model1_output': 'O1'
                }

        class Model2(h1.Model):
            def predict(self, inputs):
                return {                    
                    'model2_input': inputs['model2'],
                    'model2_output': 'O2'
                }

        class Model3(h1.Model):
            def predict(self, inputs):
                return {
                    'model3_input': inputs['model3'],
                    'model3_output': 'O3'
                }

        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(Model1())
                        .add(Model2())
                        .add(Model3())                                                
                )

                self.end()
        
        g = MyGraph()
    
        result = g.predict(data={ 'model1': 'i1', 'model2': 'i2', 'model3': 'i3' })
        self.assertEqual(result['model1_input'], 'i1')
        self.assertEqual(result['model1_output'], 'O1')
        self.assertEqual(result['model2_input'], 'i2')
        self.assertEqual(result['model2_output'], 'O2')
        self.assertEqual(result['model3_input'], 'i3')
        self.assertEqual(result['model3_output'], 'O3')

    def test_dummy_model(self):
        class MyGraph(h1.Graph):
            def __init__(self):
                super().__init__()

                (
                    self
                        .start()
                        .add(DummyModel())
                        .add(DummyModel())
                        .add(DummyModel())
                )

                self.end()

        g = MyGraph()
        result = g.predict({})
        self.assertEqual(result, {})
