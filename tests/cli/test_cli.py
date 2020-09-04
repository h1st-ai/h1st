from unittest import TestCase
import tempfile
from distutils import dir_util
import pathlib
import subprocess

from h1st.cli.project import new_project

class CliTestCase(TestCase):
    def test_new_project(self):
        tempdir = tempfile.mkdtemp()
        try:
            project_path, _ = new_project("test", tempdir)

            p = pathlib.Path(project_path)

            self.assertTrue(p.exists())
            self.assertTrue((p / 'test_graph.py').exists())
        finally:
            dir_util.remove_tree(tempdir)

    def test_cli_smoketest(self):
        """
        Verify that the project generates by framework CLI does not throw any exception
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.check_call(
                ["h1", "new-project", "AutoCyber"],
                cwd=tmpdir
            )

            subprocess.check_call(
                ["h1", "new-model", "Model2"],
                cwd=tmpdir + '/AutoCyber'
            )

            # test if we can import the graph
            subprocess.check_call(
                ["python", "-m", "autocyber_graph"],
                cwd=tmpdir + '/AutoCyber',
            )

            subprocess.check_call(
                ["python", "-m", "models.model2"],
                cwd=tmpdir + '/AutoCyber'
            )

            subprocess.check_call(
                ["nose2"],
                cwd=tmpdir + '/AutoCyber'
            )
