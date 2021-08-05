__all__ = ['SchemaValidator']

from h1st.unused.schema.schema_inferrer import SchemaInferrer
from h1st.unused.schema.schema_validation_result import SchemaValidationResult
from h1st.unused.schema.validators.field_validator import FieldValidator
from h1st.unused.schema.validators.list_validator import ListValidator
from h1st.unused.schema.validators.numpy_validator import NumpySchemaValidator
from h1st.unused.schema.validators.pyarrow_validator import PyArrowSchemaValidator
from h1st.unused.schema.validators.type_helper import validate_python_type, type_name, is_list_type, get_list_type
from h1st.unused.schema.validators.union_validator import UnionValidator


class SchemaValidator:
    _validators = [
        PyArrowSchemaValidator,
        NumpySchemaValidator,
        UnionValidator,
        ListValidator,
        FieldValidator,
    ]

    def validate(self, data, schema) -> SchemaValidationResult:
        """
        Validate the given data with a schema.::

            data = [1, 2, 3, 4, 5]  # list of integer
            schema = {'type': list, 'item': str}
            result = SchemaValidator().validate(data, schema)
            print(result.errors)

        The current implementation infers the schema from the data, and then compare two schema together.
        In the future, we will use data directly to compare the schema.

        :param data: data to be validated, it can be anything.
        :param schema: target schema
        :return: validation result
        """

        inferrer = SchemaInferrer()
        return self.validate_downstream_schema(inferrer.infer_schema(data), schema)

    def validate_downstream_schema(self, source, target) -> SchemaValidationResult:
        """
        Compare two schema and return the differences.

        :param source: source schema
        :param target: target schema
        :return: validation result
        """
        return SchemaValidationResult(self._validate(source, target))

    def _validate(self, upstream, downstream) -> list:
        # when there is one schema missing, ignore the validation
        if upstream is None or downstream is None:
            return []

        # normalize schema to dict type
        upstream = self._normalize_type(upstream)
        downstream = self._normalize_type(downstream)

        result = []
        if not validate_python_type(upstream.get('type'), downstream.get('type')):
            result.append(f'Expects {type_name(downstream)}, receives {type_name(upstream)}')
            return result

        for klass in self._validators:
            validator = klass()
            validator.validate = self._validate

            if validator.is_applicable(downstream):
                result += validator.validate_type(upstream, downstream)
                break

        return result

    def _normalize_type(self, t):
        """
        Normalize type to dict type format
        """
        if isinstance(t, dict):
            return t

        if is_list_type(t):
            return {
                'type': list,
                'item': get_list_type(t)
            }

        return {'type': t}
