from unittest import TestCase
from unittest.mock import patch
from h1st.core import Graph, Action, Model
from h1st.schema.testing import setup_schema_tests


class SchemaTestingTestCase(TestCase):
    @patch('h1st.schema.testing.ValidationSchema')
    def test_test_case_generator(self, mock_graph_schema):

        mock_graph_schema.load.return_value = {}

        class MyTestModel(Model):
            pass

        g = Graph()
        g.start()
        g.add(Model())
        g.end()

        scopes = {}
        setup_schema_tests(g, scopes)
        self.assertEqual({}, scopes)

        mock_graph_schema.load.return_value = {
            'Model': {
                'test_input': {
                    'test': 1
                },
                'expected_output': {
                    'schema': {
                        'type': dict,
                    },
                }
            }
        }
        setup_schema_tests(g, scopes)
        self.assertTrue('Graph_Model_output' in scopes)

    @patch('h1st.schema.testing.ValidationSchema')
    def test_test_case_runner(self, mock_graph_schema):
        class MyTestModel(Model):
            def predict(self, input_data):
                return {
                    "result": sum(input_data['inputs'])
                }

        g = Graph()
        g.start()
        g.add(Model())
        g.end()

        test_data = []
        schema = {
            'Model': {
                'test_input': {},
                'expected_output': {
                    'schema': {
                        'type': dict,
                    }
                }
            }
        }

        mock_graph_schema.load.return_value = schema
        g._schema = schema

        scopes = {}
        setup_schema_tests(g, scopes)
        test_class = scopes['Graph_Model_output']

        result = test_class('runTest')()
        self.assertEqual(0, len(result.errors))

        schema['Model']['test_input']['inputs'] = [1, 2, 3]
        result = test_class('runTest')()
        self.assertEqual(0, len(result.errors))

        schema['Model']['expected_output']['schema']['type'] = list
        result = test_class('runTest')()
        self.assertTrue("Expects list, receives dict" in result.failures[0][1])
