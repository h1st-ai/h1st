from unittest import TestCase
import sys
import os
import pathlib
import tempfile
from distutils import dir_util
from h1st.core.context import init, discover_h1st_project


class TestContext(TestCase):
    def test_explicit_init_model_repo(self):
        from h1st.model.repository import ModelRepository
        init(MODEL_REPO_PATH=".model")
        mm = ModelRepository.get_model_repo()
        assert(mm._storage.storage_path == ".model")
        delattr(ModelRepository, 'MODEL_REPO')

    def test_discover_package(self):
        try:
            syspath = sys.path
            cwd = os.getcwd()
            tmp_name = tempfile.mkdtemp()

            p = pathlib.Path(tmp_name)
            prj_folder = (p / "MyProject")
            prj_folder.mkdir()
            (prj_folder / "__init__.py").touch()
            (prj_folder / "graph.py").touch()
            (prj_folder / "config.py").touch()
            model_dir = (prj_folder / "models")
            model_dir.mkdir()
            (model_dir / "__init__.py").touch()
            nb_dir = (prj_folder / "notebooks")
            nb_dir.mkdir()

            os.chdir(tmp_name)

            self.assertIsNone(discover_h1st_project()[1])
            self.assertEqual(str(p), discover_h1st_project(prj_folder)[1])
            self.assertEqual(str(p), discover_h1st_project(model_dir)[1])
            self.assertEqual(str(p), discover_h1st_project(nb_dir)[1])
        finally:
            os.chdir(cwd)
            dir_util.remove_tree(tmp_name)
            sys.path = syspath
