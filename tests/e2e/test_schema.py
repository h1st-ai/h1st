import os
from unittest import TestCase, skip
import subprocess


class SchemaE2ETest(TestCase):
    def test_e2e_schema(self):
        example_path = os.path.join(
            os.path.dirname(__file__),
            "schema_sample"
        )

        subprocess.check_call(
            ["nose2", "-v"],
            cwd=example_path
        )
