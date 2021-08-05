import pyarrow as pa

from h1st.unused.schema.validators.base import BaseValidator


class PyArrowSchemaValidator(BaseValidator):
    """
    Validate pyarrow schema
    """
    def is_applicable(self, schema):
        return isinstance(schema.get('type'), pa.Schema)

    def validate_type(self, upstream, downstream):
        result = []
        upstream = upstream['type']
        downstream = downstream['type']

        for name in downstream.names:
            # check if field is available
            if name not in upstream.names:
                result.append(f'Field "{name}" is missing')
                continue

            field = downstream.field(name)
            upstream_field = upstream.field(name)

            # check if type is compatible
            # TODO: check if we can upcast
            # TODO: pyarrow dict, struct
            for err in self.validate(upstream_field.type, field.type):
                result.append(f'Field "{name}": {err}')

        return result
