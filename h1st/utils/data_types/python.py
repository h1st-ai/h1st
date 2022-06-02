"""Python data types."""


from typing import Union
from typing import Tuple   # Py3.9+: use built-ins


__all__ = (
    'PY_NUM_TYPES', 'PyNumType',
    'PY_POSSIBLE_FEATURE_TYPES', 'PyPossibleFeatureType',
    'PY_LIST_OR_TUPLE',
)


PY_NUM_TYPES: Tuple[type] = float, int
PyNumType = Union[float, int]

PY_POSSIBLE_FEATURE_TYPES: Tuple[type] = bool, float, int, str
PyPossibleFeatureType = Union[bool, float, int, str]

PY_LIST_OR_TUPLE: Tuple[type] = list, tuple
