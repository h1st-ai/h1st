import inspect
from unittest import TestCase

from h1st.unused.schema.schema_validation_result import SchemaValidationResult
from h1st.unused.schema.validation_schema import ValidationSchema


def setup_schema_tests(graph, scope, prepare_func=None):
    """
    Helper function to create schema test cases from a graph

    :param graph: target graph
    :param scope: pass in ``globals``
    """
    try:
        schema = ValidationSchema.load(graph)
        graph_name = graph.__class__.__name__
        scope_name = scope.get('__name__') or 'test_schema'
        prepare_test_data = _make_prepare_func(prepare_func)

        # only define test cases when schema and sample data are provided
        for node in graph.nodes.__dict__.values():
            node_schema_info = schema.get(node.id)

            if node_schema_info:
                name = f"{graph_name}_{node.id}_output"
                scope[name] = _make_test_case(
                    name, scope_name,
                    node, node_schema_info,
                    prepare_test_data,
                )
    except ModuleNotFoundError:
        pass  # no schema module is defined, it is safely to skip


def _make_prepare_func(prepare_func):
    """
    Generate a function to prepare test data
    :returns: function
    """

    def prepare_test_data(node, item, schema):
        if not prepare_func:
            return item

        sig = inspect.signature(prepare_func)
        kwargs = {}
        if 'node' in sig.parameters:
            kwargs['node'] = node

        result = prepare_func(item, **kwargs)

        if result is None:
            result = item

        return result

    return prepare_test_data


def _make_test_case(name, scope_name, node, schema_info, prepare_test_data):
    """
    Generate a schema test case for given node

    :returns: generated test case class
    """

    class IOTestCase(TestCase):
        def __init__(self, method):
            self.method = method
            self._name = scope_name + "." + name
            super().__init__('runTest')

        def runTest(self):
            schema = schema_info['expected_output']['schema']
            test_data = schema_info['test_input']

            if schema == ...:
                self.skipTest('Schema is not yet defined')

            item = prepare_test_data(node, test_data, schema)

            result = node.validate_output(item, schema=schema)

            if result is None:
                pass  # no verification was implemented
            elif not isinstance(result, SchemaValidationResult):
                self.fail('return value is not SchemaValidationResult')
            elif not result:
                err_msg = '\n'.join(result.errors)
                self.fail(f"\n\n----\nTest data:\n{err_msg}\n----\n")

        def __repr__(self):
            return self._name

        id = __str__ = __repr__

    return IOTestCase
