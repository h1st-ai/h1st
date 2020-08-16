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

class DecisionNodeTestCase(TestCase):
    '''
    Test script:
        given input as array of value, decision will split value >= 10 to yes/no branches
        then each downstream node will calculate its sum

    '''

    def setUp(self):
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
        
        self._g = MyGraph()

    def test_decision_yes_no(self):
        result = self._g.predict(data={'values': [10, 5, 6, 20]})
        self.assertEqual(result['yes_sum'], 30)
        self.assertEqual(result['no_sum'], 11)

    def test_decision_yes_only(self):
        result = self._g.predict(data={'values': [10, 15, 16, 20]})
        self.assertEqual(result['yes_sum'], 61)

    def test_decision_no_only(self):
        result = self._g.predict(data={'values': [1, 2, 3, 4]})
        self.assertEqual(result['no_sum'], 10)

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
