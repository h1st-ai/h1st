"""
Utilities function to work with python types
"""

from typing import Union, List
import pyarrow as pa


def type_name(t) -> str:
    """
    Return a human readable string for a type
    """
    if isinstance(t, dict):
        return type_name(t.get('type'))
    if isinstance(t, pa.Schema):
        return 'schema'
    if isinstance(t, type):
        return t.__name__

    return str(t)


def is_union_type(t) -> bool:
    """
    Return True if type is ``Union`` python type
    """
    if isinstance(t, dict):
        t = t.get('type')

    return hasattr(t, '__origin__') and t.__origin__ is Union


def is_optional_type(t) -> bool:
    """
    Return True if type is ``Optional`` python type
    """
    if isinstance(t, dict):
        t = t.get('type')

    return is_union_type(t) and len(t.__args__) == 2 and t.__args__[1] == type(None)


def is_list_type(t) -> bool:
    """
    Return True if ``t`` is ``List`` python type
    """
    # print(t, getattr(t, '__origin__', None) is list)
    return t == list or is_pa_type(t, pa.types.is_list) or (
        hasattr(t, '__origin__') and t.__origin__ in (list, List)
    ) or (
        isinstance(t, dict) and is_list_type(t.get('type'))
    )


def get_list_type(t):
    """
    Retrieve the type annotation from ``List``
    """
    if is_pa_type(t, pa.types.is_list):
        return t.value_type
    if hasattr(t, '__origin__') and t.__origin__ in (list, List):
        return t.__args__[0]
    if isinstance(t, dict):
        return t.get('item')

    return None


def is_pa_type(t, check):
    """
    This function do additonal check on pyarrow type to make this works with python type::

    >>> is_pa_type(pa.float64(), pa.types.is_float64)
    >>> True

    :param t: target type
    :param check: checker function
    """
    return isinstance(t, pa.DataType) and check(t)


_python_types = {
    int: pa.types.is_integer,
    str: pa.types.is_string,
    float: pa.types.is_floating,
    bytes: pa.types.is_float_value,
}


def validate_python_type(source, target) -> bool:
    """
    Validate native python type and return True if two types are compatible

    :returns: True if two type are compatible
    """
    if source == target:
        return True
    if is_union_type(source) or is_union_type(target):
        return True
    if isinstance(source, pa.Schema) and isinstance(target, pa.Schema):
        return True
    if target in _python_types:
        return is_pa_type(source, _python_types[target])
    if source in _python_types:
        return is_pa_type(target, _python_types[source])

    # TODO: integer casting, float casting, date casting

    return False
