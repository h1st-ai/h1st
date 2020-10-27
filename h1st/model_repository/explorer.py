import os
import importlib
import pathlib
import inspect
import re
import sys
import logging

from concurrent.futures import ProcessPoolExecutor
from h1st.core.context import discover_h1st_project
from h1st.core.model import Model

logger = logging.getLogger(__name__)
MODEL_FILE_NAME = re.compile(r"^[^_].*_(classifier|detector|model).py$")


def _discover_module(data):
    module_name, filename = data
    result = {}
    try:
        module = importlib.import_module(module_name)
        for attr in dir(module):
            value = getattr(module, attr)

            if inspect.isclass(value) and issubclass(value, Model):
                fullname = value.__name__

                if value.__module__:
                    fullname = f"{value.__module__}.{fullname}"

                hyperparameter_def = getattr(value, 'hyperparameter', {})

                result[fullname] = {
                    'id': fullname,
                    'name': value.__name__,
                    'tunable': hyperparameter_def.get('target_metrics') is not None,
                    'filename': filename,
                    'hyperparameters': hyperparameter_def.get('tuning_param', {}),
                    'target_metrics': hyperparameter_def.get('target_metrics', {}),
                }
    except ImportError:
        logger.exception(f'Unable to import module {module_name}')
    except SyntaxError:
        logger.exception(f'Unable to import module {module_name}')

    return result


class ModelExplorer:
    """
    Utility class to discover model class in a project
    """
    def discover_models(self):
        project_root, _ = discover_h1st_project()
        if not project_root:
            project_root = os.getcwd()

        if project_root not in sys.path:
            sys.path.append(str(project_root))

        project_root = pathlib.Path(project_root)
        model_files = []

        if (project_root / "__init__.py").exists():
            sys.path.append(str(project_root.parent))
            try:
                importlib.import_module(project_root.name)
                package_root = project_root.name
            except ImportError:
                package_root = ""
        else:
            package_root = ""

        for f in project_root.glob("*.py"):
            if MODEL_FILE_NAME.match(f.name):
                model_files.append(f)

        if (project_root / "models").exists():
            model_files += list((project_root / "models").glob("*.py"))

        # convert to module
        for i, model_file in enumerate(model_files):
            model_package = str(model_file)[len(str(project_root)) + 1:-3]
            model_package = model_package.replace(os.sep, '.')

            if package_root:
                model_package = f"{package_root}.{model_package}"

            model_files[i] = (model_package, model_file)

        result = {}
        with ProcessPoolExecutor(max_workers=4) as pool:
            for res in pool.map(_discover_module, model_files):
                result.update(res)

        return result


if __name__ == "__main__":
    explorer = ModelExplorer()
    print(explorer.discover_models())
