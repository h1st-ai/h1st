from numpy import floating, integer, isnan, isreal, isscalar, ndarray
from pandas import DataFrame
from uuid import UUID

from .models import DataSet, NumPyArray, PandasDataFrame


def load_data_set_pointers_as_json(data):
    if isinstance(data, dict):
        return {k: load_data_set_pointers_as_json(v)
                for k, v in data.items()}

    elif isinstance(data, (list, tuple)):
        return [load_data_set_pointers_as_json(i)
                for i in data]

    elif isinstance(data, str):
        try:
            uuid = UUID(hex=data, version=4)
        except ValueError:
            uuid = None

        return DataSet.objects.get(uuid=uuid).json \
            if uuid \
          else data

    else:
        return data


def save_numpy_arrays_and_pandas_dfs_as_data_set_pointers(data):
    if isinstance(data, dict):
        return {k: save_numpy_arrays_and_pandas_dfs_as_data_set_pointers(v)
                for k, v in data.items()}

    elif isinstance(data, (list, tuple)):
        return [save_numpy_arrays_and_pandas_dfs_as_data_set_pointers(i)
                for i in data]

    elif isinstance(data, ndarray):
        return str(NumPyArray.objects.create(
                    dtype=str(data.dtype),
                    json=save_numpy_arrays_and_pandas_dfs_as_data_set_pointers(
                            data.tolist())).uuid)

    elif isinstance(data, DataFrame):
        return str(PandasDataFrame.objects.create(
                    json=PandasDataFrame.jsonize(data)).uuid)

    elif isscalar(data):
        if isreal(data) and isnan(data):
            return None

        elif isinstance(data, floating):
            return float(data)

        elif isinstance(data, integer):
            return int(data)

        else:
            return data

    else:
        return data
