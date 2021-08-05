from h1st.unused.schema.validators.base import BaseValidator
from h1st.unused.schema.validators.type_helper import is_list_type, type_name, get_list_type


class ListValidator(BaseValidator):
    """
    Validate python list type
    """

    def is_applicable(self, schema):
        return is_list_type(schema)

    def validate_type(self, upstream, downstream):
        result = []
        if not is_list_type(upstream):
            upstream_type = upstream['type']
            result.append(f'Expects list, receives {type_name(upstream_type)}')
        else:
            downstream_field = get_list_type(downstream)
            upstream_field = get_list_type(upstream)

            for err in self.validate(upstream_field, downstream_field):
                result.append(f'List type mismatch, {err}')

        return result
