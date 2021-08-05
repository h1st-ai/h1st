import numpy  as np

from h1st.unused.schema.validators.base import BaseValidator


class NumpySchemaValidator(BaseValidator):
    """
    Validate numpy schema
    """
    def is_applicable(self, schema):
        return schema.get('type') == np.ndarray

    def validate_type(self, upstream, downstream):
        result = []
        for err in self.validate(upstream.get('item'), downstream.get('item')):
            result.append(f'Item type mismatch, {err}')

        upstream_shape = upstream.get('shape', None)
        downstream_shape = downstream.get('shape', None)

        # validate shape
        if upstream_shape and downstream_shape:
            if len(upstream_shape) != len(downstream_shape):
                result.append(f'Expects shape {downstream_shape}, receives shape {upstream_shape}')
            else:
                for i, shape in enumerate(downstream_shape):
                    if shape is not None and upstream_shape[i] is not None and upstream_shape[i] != shape:
                        result.append(f'Expects shape {downstream_shape}, receives shape {upstream_shape}')
                        break

        return result
