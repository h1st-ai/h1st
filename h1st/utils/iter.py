"""Iterables-related utilities."""


import collections
from typing import Any

import numpy
import tensorflow


__all__ = ('to_iterable',)


def to_iterable(obj: Any, /, *, iterable_type=tuple) -> collections.Iterable:
    # pylint: disable=invalid-name
    """Return non-string iterable collection of specified type."""
    if isinstance(obj, iterable_type):
        return obj

    if isinstance(obj, collections.Iterable) and \
            (not isinstance(obj, (str, tensorflow.Tensor))):
        return iterable_type(obj)

    if iterable_type is tuple:
        return (obj,)

    if iterable_type is list:
        return [obj]

    if iterable_type is set:
        return {obj}

    if iterable_type is numpy.ndarray:
        return numpy.array((obj,))

    raise TypeError(f'*** INVALID iterable_type {iterable_type} ***')
