from unittest import TestCase
from datetime import datetime
import pyarrow as pa
import numpy as np
import pandas as pd

from h1st.unused.schema.schema_inferrer import SchemaInferrer


class SchemaInferrerTestCase(TestCase):
    def test_infer_python(self):
        inferrer = SchemaInferrer()

        self.assertEqual(inferrer.infer_schema(1), pa.int64())
        self.assertEqual(inferrer.infer_schema(1.1), pa.float64())

        self.assertEqual(inferrer.infer_schema({
            'test1': 1,
            'test2': "hello",
            'test3': b"hello",
            'today': datetime.now(),
        }), {
            'type': dict,
            'fields': {
                'test1': pa.int64(),
                'test2': pa.string(),
                'test3': pa.binary(),
                'today': pa.date64(),
            }
        })

        self.assertEqual(inferrer.infer_schema((
            1, 2, 3
        )), pa.list_(pa.int64()))

        self.assertEqual(inferrer.infer_schema((
            1.2, 1.3, 1.4
        )), pa.list_(pa.float64()))

        table = pa.Table.from_arrays(
            [pa.array([1, 2, 3]), pa.array(["a", "b", "c"])],
            ['c1', 'c2']
        )
        self.assertEqual(inferrer.infer_schema(table), table.schema)

    def test_infer_numpy(self):
        inferrer = SchemaInferrer()
        self.assertEqual(inferrer.infer_schema(np.random.random((100, 28, 28))), {
            'type': np.ndarray,
            'item': pa.float64(),
            'shape': (None, 28, 28)
        })

        self.assertEqual(inferrer.infer_schema(np.array(["1", "2", "3"])), {
            'type': np.ndarray,
            'item': pa.string()
        })

    def test_infer_dataframe(self):
        inferrer = SchemaInferrer()
        df = pd.DataFrame({
            'f1': [1, 2, 3],
            'f2': ['a', 'b', 'c'],
            'f3': [0.1, 0.2, 0.9]
        })

        self.assertEqual(inferrer.infer_schema(df), {
            'type': pd.DataFrame,
            'fields': {
                'f1': pa.int64(),
                'f2': pa.string(),
                'f3': pa.float64()
            }
        })

        df = pd.DataFrame({
            'Timestamp': [1.1, 2.2, 3.1],
            'CarSpeed': [0.1, 0.2, 0.9],
            'Gx': [0.1, 0.2, 0.9],
            'Gy': [0.1, 0.2, 0.9],
            'Label': ['1', '0', '1']
        })

        self.assertEqual(inferrer.infer_schema(df), {
            'type': pd.DataFrame,
            'fields': {
                'Timestamp': pa.float64(),
                'CarSpeed': pa.float64(),
                'Gx': pa.float64(),
                'Gy': pa.float64(),
                'Label': pa.string(),
            }
        })

        self.assertEqual(inferrer.infer_schema(pd.Series([1, 2, 3])), {
            'type': pd.Series,
            'item': pa.int64()
        })

    def test_infer_dict(self):
        inferrer = SchemaInferrer()
        self.assertEqual(inferrer.infer_schema({
            'test': 123,
        }), {
            'type': dict,
            'fields': {
                'test': pa.int64(),
            }
        })

        self.assertEqual(inferrer.infer_schema({
            'test': 123,
            'indices': [1, 2, 3]
        }), {
            'type': dict,
            'fields': {
                'test': pa.int64(),
                'indices': pa.list_(pa.int64())
            }
        })

        self.assertEqual(inferrer.infer_schema({
            'results': pd.DataFrame({
                'CarSpeed': [0, 1, 2],
                'Label': ['a', 'b', 'c']
            })
        }), {
            'type': dict,
            'fields': {
                'results': {
                    'type': pd.DataFrame,
                    'fields': {
                        'CarSpeed': pa.int64(),
                        'Label': pa.string(),
                    }
                }
            }
        })

    def test_infer_list(self):
        inferrer = SchemaInferrer()
        self.assertEqual(inferrer.infer_schema([
            {'test': 123},
            {'test': 345},
        ]), {
            'type': list,
            'item': {
                'type': dict,
                'fields': {
                    'test': pa.int64()
                }
            }
        })
