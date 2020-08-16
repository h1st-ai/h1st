from typing import Union, Optional, List
from unittest import TestCase
import pyarrow as pa
import pandas as pd
import numpy as np
from h1st.schema.schema_validator import SchemaValidator


dummy = lambda: None


class SchemaTestCase(TestCase):
    def test_validate_schema(self):
        # empty schema
        self.assertTrue(SchemaValidator().validate_downstream_schema(pa.schema([]), pa.schema([])) == [])
        self.assertTrue(SchemaValidator().validate_downstream_schema({}, {}) == [])

        self.assertTrue(SchemaValidator().validate_downstream_schema(pa.schema([
            ('f1', pa.int16())
        ]), None) == [])

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(None, pa.schema([])),
            [],
        )

        # self.assertEqual(
        #     SchemaValidator().validate_downstream_schema({}, pa.schema([])).errors,
        #     ['Expects schema, receives {}'],
        # )

        # field is not available
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.schema([('f1', pa.int32())]),
                pa.schema([('f2', pa.int32())]),
            ).errors,
            ['Field "f2" is missing'],
        )

        # field is not compatible
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.schema([('f1', pa.string())]),
                pa.schema([('f1', pa.int32())]),
            ),
            ['Field "f1": Expects int32, receives string'],
        )

        # same schema
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.schema([('f1', pa.int32())]),
                pa.schema([('f1', pa.int32())]),
            ),
            [],
        )

        # subset of schema
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.schema([('f1', pa.int32(), ('f2', pa.int32()))]),
                pa.schema([('f1', pa.int32())]),
            ),
            [],
        )

    def test_dataframe(self):
        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame},
            {'type': pd.DataFrame}
        ).errors, [])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame},
            {'type': list}
        ).errors, ['Expects list, receives DataFrame'])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame, 'fields': {
                'abc': str,
                'def': str,
                'myfield': int,
            }},
            {'type': pd.DataFrame, 'fields': {
                'abc': int,
                'def': {'type': str},
                'myfield': float,
            }},
        ).errors, ['Field abc: Expects int, receives str', 'Field myfield: Expects float, receives int'])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame, 'fields': {
                'abc': str,
            }},
            pd.DataFrame,
        ).errors, [])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame, 'fields': {
                'abc': str,
            }},
            {'type': pd.DataFrame, 'fields': {
                'abc': str,
                'def': Optional[str],  # optional allows missing column
            }},
        ).errors, [])

        self.assertEqual(
            SchemaValidator().validate_downstream_schema({
                'type': pd.DataFrame,
                'fields': {
                    'Timestamp': pa.float64(),
                    'CarSpeed': pa.float64(),
                    'Gx': pa.float64(),
                    'Gy': pa.float64(),
                    'Label': pa.string(),
                }
            }, {
                'type': pd.DataFrame,
                'fields': {
                    'Timestamp': float,
                    'Label': str,
                }
            }).errors,
            []
        )

    def test_dict_schema(self):
        self.assertEqual(SchemaValidator().validate_downstream_schema({}, {}), [])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': list},
            {'type': dict}
        ).errors, ['Expects dict, receives list'])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': pd.DataFrame},
            {'type': dict}
        ).errors, ['Expects dict, receives DataFrame'])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': dict},
            {
                'type': dict,
                'fields': {
                    'abc': str,
                }
            }
        ).errors, ['Field abc is missing'])

        self.assertEqual(SchemaValidator().validate_downstream_schema(
            {'type': dict, 'fields': {'abc': int}},
            {
                'type': dict,
                'fields': {
                    'abc': str,
                }
            }
        ).errors, ['Field abc: Expects str, receives int'])

        # self.assertEqual(SchemaValidator().validate_downstream_schema({
        # }, {
        #     'df': pa.schema([('f1', pa.int32())]),
        # }), [])

        # self.assertEqual(SchemaValidator().validate_downstream_schema({
        #     'df': pa.schema([]),
        # }, {
        #     'df': pa.schema([('f1', pa.int32())]),
        # }).errors, ['Key "df": Field "f1" is missing'])

    def test_list_schema(self):
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                float,
                {'type': list},
            ).errors,
            ['Expects list, receives float']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.list_(pa.int64()),
                pa.list_(pa.float64()),
            ).errors,
            ['List type mismatch, Expects double, receives int64']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                pa.list_(pa.int64()),
                List[int],
            ).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(List[int], List[int]).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(List[float], List[float]).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(List[str], List[int]).errors,
            ['List type mismatch, Expects int, receives str']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': list, 'item': float},
                List[str],
            ).errors,
            ['List type mismatch, Expects str, receives float']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                List[str],
                {'type': list, 'item': float},
            ).errors,
            ['List type mismatch, Expects float, receives str']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': list, 'item': str},
                {'type': list, 'item': float},
            ).errors,
            ['List type mismatch, Expects float, receives str']
        )

    def test_python_type(self):
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(str, int).errors,
            ["Expects int, receives str"]
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(str, Optional[str]).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(str, pa.string()).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(int, pa.string()).errors,
            ["Expects string, receives int"]
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(str, Union[str, int]).errors,
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(float, Union[str, int]).errors,
            ["Expects typing.Union[str, int], receives <class 'float'>"]
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(Union[float, bytes], Union[str, int]).errors,
            ["Expects typing.Union[str, int], receives typing.Union[float, bytes]"]
        )

    def test_tensor(self):
        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                float,
                {'type': np.ndarray, 'item': pa.int32()},
            ).errors,
            ['Expects ndarray, receives float']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32()},
                {'type': np.ndarray, 'item': pa.int32()},
            ),
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32()},
                {'type': np.ndarray, 'item': pa.float64()},
            ).errors,
            ['Item type mismatch, Expects double, receives int32']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2)},
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2)},
            ),
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (None, 2)},
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2)},
            ),
            []
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (None, None, 4)},
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (None, None, 8)},
            ),
            ['Expects shape (None, None, 8), receives shape (None, None, 4)']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (5, 2)},
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2)},
            ),
            ['Expects shape (2, 2), receives shape (5, 2)']
        )

        self.assertEqual(
            SchemaValidator().validate_downstream_schema(
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2, 2)},
                {'type': np.ndarray, 'item': pa.int32(), 'shape': (2, 2)},
            ),
            ['Expects shape (2, 2), receives shape (2, 2, 2)']
        )
