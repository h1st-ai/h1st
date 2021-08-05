from h1st.unused.schema.validators.base import BaseValidator
from h1st.unused.schema.validators.type_helper import is_union_type


class UnionValidator(BaseValidator):
    """
    Validate python ``Union`` type
    """

    def is_applicable(self, schema):
        return is_union_type(schema)

    def validate_type(self, upstream, downstream):
        result = []

        downstream_type = downstream['type']
        upstream_type = upstream['type']
        if is_union_type(upstream_type) and len(set(upstream_type.__args__) & set(upstream_type.__args__)) == 0:
            result.append(f'Expects {upstream_type}, receives {upstream_type}')
        elif upstream_type not in downstream_type.__args__:
            result.append(f'Expects {downstream_type}, receives {upstream_type}')

        return result
