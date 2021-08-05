import importlib

from h1st.exceptions.exception import SchemaException
from h1st.unused.schema import SchemaValidationResult, SchemaValidator


class ValidationSchema:
    def __init__(self, schema=None):
        self._schema = schema or {}

    def __getitem__(self, node_id):
        return self._schema.get(node_id, {})

    def __contains__(self, node_id):
        return node_id in self._schema

    def get(self, node_id):
        """
        Retrieve schema for a node via its ID
        """
        return self._schema.get(node_id, {})

    def validate_output(self, node_id: str, data=None) -> SchemaValidationResult:
        return self._validate(node_id, 'output', data)

    def _validate(self, node_id: str, io: str, data=None) -> SchemaValidationResult:
        ''' io = 'input' | 'output' '''

        result = SchemaValidationResult()

        io_info = self[node_id].get(io)
        if io_info:
            schema = io_info.get('schema')
            data = data or io_info.get('test_data')

            result.merge(
                SchemaValidator().validate(data, schema),
            )

        return result

    @staticmethod
    def load(graph: 'Graph') -> 'ValidationSchema':
        """
        Discover associated schema file of a graph. The schema file is a
        python module placed in the same level of graph module
        """
        prefix = graph.__class__.__module__.split(".")
        prefix.pop()
        config_module_name = ".".join(prefix) + ".config"
        if config_module_name == ".config":
            config_module_name = "config"

        schema_name = graph._node_validation_schema_name  # XXX
        try:
            module = importlib.import_module(config_module_name)
            schema = getattr(module, schema_name, {})

            if not isinstance(schema, dict):
                raise SchemaException(f'Schema "{schema_name}" must be a dict')
        except:
            raise SchemaException(f'Schema "{schema_name}" must be defined in config.py')

        return ValidationSchema(schema)
