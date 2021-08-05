import pandas as pd

from h1st.unused.schema.validators.base import BaseValidator
from h1st.unused.schema.validators.type_helper import is_optional_type


class FieldValidator(BaseValidator):
    """
    Validate python dictionary and dataframe type
    """
    def is_applicable(self, schema):
        return schema.get('type') == pd.DataFrame or schema.get('type') == dict

    def validate_type(self, upstream, downstream):
        result = []
        fields_downstream = downstream.get('fields', {})
        fields_upstream = upstream.get('fields', {})

        for name, field_type in fields_downstream.items():
            if name not in fields_upstream:
                if not is_optional_type(field_type):
                    result.append(f'Field {name} is missing')
            else:
                for err in self.validate(fields_upstream[name], field_type):
                    result.append(f"Field {name}: {err}")

        return result
