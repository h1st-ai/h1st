from datetime import datetime

import numpy as np
import pandas as pd
import pyarrow as pa


__all__ = ['SchemaInferrer']

_python_mapping = {
    int: pa.int64,
    float: pa.float64,
    str: pa.string,
    bytes: pa.binary,
    datetime: pa.date64,
}

_SAMPLE_SIZE = 1000


class SchemaInferrer:
    def infer_schema(self, data):
        """
        Infer a schema for a given data input. The schema can be used to test with schema validator.
        This function currently supports DataFrame, Numpy, Dictionary, List and basic python types.::

            data = pandas.DataFrame(...)
            schema = infer_schema(data)

        This function returns None if it can not infer the schema.
        """
        schema = None

        if data is None:
            schema = pa.null()
        elif isinstance(data, dict):
            schema = {
                'type': dict,
                'fields': {}
            }

            for key, value in data.items():
                schema['fields'][key] = self.infer_schema(value)
        elif isinstance(data, pd.DataFrame):
            schema = {
                'type': pd.DataFrame,
                'fields': {}
            }

            # sample the table to get the schema
            pa_schema = pa.Table.from_pandas(data[:_SAMPLE_SIZE], preserve_index=False).schema
            for i, name in enumerate(pa_schema.names):
                schema['fields'][name] = pa_schema.types[i]
        elif isinstance(data, pd.Series):
            schema = {
                'type': pd.Series,
                'item': pa.Array.from_pandas(data).type,
            }
        elif isinstance(data, np.ndarray):
            pa_type = pa.from_numpy_dtype(data.dtype) if data.dtype.num != 17 else pa.string()

            if len(data.shape) == 1:  # 1d array
                schema = {
                    'type': np.ndarray,
                    'item': pa_type,
                }
            else:
                shape = [v if i != 0 else None for i, v in enumerate(data.shape)]
                schema = {
                    'type': np.ndarray,
                    'item': pa_type,
                    'shape': tuple(shape),
                }
        elif isinstance(data, pa.Table):
            schema = data.schema
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            # try to infer type of the data
            current_type = self.infer_schema(data[0])
            for i in range(1, min(len(data), _SAMPLE_SIZE)):
                new_type = self.infer_schema(data[i])

                if new_type != current_type:
                    current_type = None
                    break

            # does not support multiple type yet
            if current_type:
                if isinstance(current_type, pa.DataType):
                    schema = pa.list_(current_type)
                else:
                    schema = {
                        'type': list,
                        'item': current_type
                    }
        elif type(data) in _python_mapping:
            schema = _python_mapping[type(data)]()
        else:
            return {'type': type(data)}

        return schema
