"""Spark SQL data types."""


from typing import Tuple   # Py3.9+: use built-ins

# pylint: disable=unused-import
from pyspark.sql.types import (   # noqa: F401
    DataType,

    NullType,

    AtomicType,

    BooleanType,

    StringType,

    BinaryType,

    NumericType,

    IntegralType,
    ByteType,
    ShortType,
    IntegerType,
    LongType,

    FractionalType,
    FloatType,
    DoubleType,
    DecimalType,

    DateType,
    TimestampType,

    # Complex Types
    ArrayType,
    MapType,
    StructField,
    StructType,

    _atomic_types, _all_atomic_types, _all_complex_types,
    _type_mappings,
    _array_signed_int_typecode_ctype_mappings,
    _array_unsigned_int_typecode_ctype_mappings,
    _array_type_mappings,
    _acceptable_types,
)


__all__ = (
    '_NULL_TYPE',
    '_BOOL_TYPE',

    '_STR_TYPE',
    '_BINARY_TYPE',

    '_TINYINT_TYPE',
    '_SMALLINT_TYPE',
    '_INT_TYPE',
    '_BIGINT_TYPE',
    '_INT_TYPES',

    '_FLOAT_TYPE',
    '_DOUBLE_TYPE',
    '_FLOAT_TYPES',

    '_NUM_TYPES',

    '_POSSIBLE_CAT_TYPES',
    '_POSSIBLE_FEATURE_TYPES',

    '_DATE_TYPE',
    '_TIMESTAMP_TYPE',
    '_DATETIME_TYPES',

    '_DECIMAL_10_0_TYPE',
    '_DECIMAL_38_18_TYPE',
    '_DECIMAL_TYPE_PREFIX',

    '_ARRAY_TYPE_PREFIX',
    '_MAP_TYPE_PREFIX',
    '_STRUCT_TYPE_PREFIX',

    '_VECTOR_TYPE',
)


__null_type: NullType = NullType()
_NULL_TYPE: str = __null_type.simpleString()
assert _NULL_TYPE == __null_type.typeName()


__bool_type: BooleanType = BooleanType()
_BOOL_TYPE: str = __bool_type.simpleString()
assert _BOOL_TYPE == __bool_type.typeName()


__str_type: StringType = StringType()
_STR_TYPE: str = __str_type.simpleString()
assert _STR_TYPE == __str_type.typeName()


__binary_type: BinaryType = BinaryType()
_BINARY_TYPE: str = __binary_type.simpleString()
assert _BINARY_TYPE == __binary_type.typeName()


__byte_type: ByteType = ByteType()
_TINYINT_TYPE: str = __byte_type.simpleString()

__short_type: ShortType = ShortType()
_SMALLINT_TYPE: str = __short_type.simpleString()

__int_type: IntegerType = IntegerType()
_INT_TYPE: str = __int_type.simpleString()
assert _INT_TYPE == int.__name__
assert __int_type.typeName().startswith(_INT_TYPE)

__long_type: LongType = LongType()
_BIGINT_TYPE: str = __long_type.simpleString()
assert __long_type.typeName() == 'long'

_INT_TYPES: Tuple[str] = _TINYINT_TYPE, _SMALLINT_TYPE, _INT_TYPE, _BIGINT_TYPE


__float_type: FloatType = FloatType()
_FLOAT_TYPE: str = __float_type.simpleString()
assert _FLOAT_TYPE == __float_type.typeName()

__double_type: DoubleType = DoubleType()
_DOUBLE_TYPE: str = __double_type.simpleString()
assert _DOUBLE_TYPE == __double_type.typeName()

_FLOAT_TYPES: Tuple[str] = _FLOAT_TYPE, _DOUBLE_TYPE


_NUM_TYPES: Tuple[str] = _INT_TYPES + _FLOAT_TYPES


_POSSIBLE_CAT_TYPES: Tuple[str] = (_BOOL_TYPE, _STR_TYPE) + _NUM_TYPES
_POSSIBLE_FEATURE_TYPES: Tuple[str] = _POSSIBLE_CAT_TYPES + _NUM_TYPES


__date_type: DateType = DateType()
_DATE_TYPE: str = __date_type.simpleString()
assert _DATE_TYPE == __date_type.typeName()

__timestamp_type: TimestampType = TimestampType()
_TIMESTAMP_TYPE: str = __timestamp_type.simpleString()
assert _TIMESTAMP_TYPE == __timestamp_type.typeName()

_DATETIME_TYPES: Tuple[str] = _DATE_TYPE, _TIMESTAMP_TYPE


__decimal_10_0_type: DecimalType = DecimalType(precision=10, scale=0)
_DECIMAL_10_0_TYPE: str = __decimal_10_0_type.simpleString()

__decimal_38_18_type: DecimalType = DecimalType(precision=38, scale=18)
_DECIMAL_38_18_TYPE: str = __decimal_38_18_type.simpleString()

_DECIMAL_TYPE_PREFIX: str = f'{DecimalType.typeName()}('


_ARRAY_TYPE_PREFIX: str = f'{ArrayType.typeName()}<'
_MAP_TYPE_PREFIX: str = f'{MapType.typeName()}<'
_STRUCT_TYPE_PREFIX: str = f'{StructType.typeName()}<'

_VECTOR_TYPE: str = 'vector'
