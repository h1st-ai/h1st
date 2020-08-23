import pathlib
import tempfile
import shutil
import re
from distutils import dir_util

import click
from colored import attr, fg


@click.command('new-project')
@click.argument('project_name',)
def new_project_cli(project_name):
    """
    CLI command to create new project
    """
    try:
        new_project(project_name, '.')
        print('Project %s%s%s is created successfully.' % (
            attr('bold'),
            project_name,
            attr('reset')
        ))
    except Exception as ex:
        print('%sError:%s %s' % (
            fg('red'),
            attr('reset'),
            ex,
        ))


@click.command('new-model')
@click.argument('model_name')
def new_model_cli(model_name):
    """
    CLI command to create new model
    """
    try:
        path = pathlib.Path('.').absolute()
        model_path = (path / 'models')

        # TODO: try to figure out the project folder if possible

        if not model_path.exists():
            raise ValueError('Please run this command in the package folder')

        class_name, module_name = _clean_name(model_name)

        if not class_name.lower().endswith("model"):
            class_name = f"{class_name}Model"

        new_model(
            class_name,
            path,
            path.name,
            module_name=module_name
        )

        print('Model %s%s%s is created successfully.' % (
            attr('bold'),
            model_name,
            attr('reset')
        ))
    except Exception as ex:
        print('%sError:%s %s' % (
            fg('red'),
            attr('reset'),
            ex,
        ))

def new_project(project_name, base_path):
    """
    Create a new project under the given base path

    :param project_name: name of the project
    :param base_path: target folder to create the project
    """
    project_name_camel_case, project_name_snake_case = _clean_name(project_name)

    class_prefix = project_name_camel_case

    path = pathlib.Path(base_path)
    project_module = path / project_name_camel_case

    if project_module.exists():
        raise ValueError(f'Folder {project_name_camel_case} already exists')

    # generate the project in a temporary folder then move to the target folder
    # to avoid cleaning up in case of error
    tmpdir = tempfile.mkdtemp()
    try:
        tmppath = pathlib.Path(tmpdir)
        graph_file = tmppath / 'graph.py'
        data_folder = tmppath / 'data'
        model_folder = tmppath / 'models'
        notebook_folder = tmppath / 'notebooks'
        visualization_folder = tmppath / 'visualization'
        test_folder = tmppath / 'tests'

        # create all folders
        visualization_folder.mkdir(exist_ok=True)
        notebook_folder.mkdir(exist_ok=True)
        model_folder.mkdir(exist_ok=True)
        data_folder.mkdir(exist_ok=True)
        test_folder.mkdir(exist_ok=True)

        # create all empty files
        (tmppath / '__init__.py').touch()
        (tmppath / 'schema.py').touch()
        (tmppath / 'config.py').touch()
        (tmppath / 'LICENSE').touch()
        (tmppath / 'README.md').touch()
        (tmppath / 'requirements.txt').touch()
        (model_folder / '__init__.py').touch()
        (visualization_folder / '__init__.py').touch()
        (test_folder / '__init__.py').touch()
        (notebook_folder / ".gitkeep").touch()
        (data_folder / '.gitkeep').touch()

        with open(graph_file, "w") as f:
            f.write(_render_init_graph_class(project_name_snake_case, class_prefix))

        with open(test_folder / "test_schema.py", "w") as f:
            f.write(_render_schema_testcase(project_name_camel_case, class_prefix))

        new_model(
            f"{class_prefix}Model",
            tmppath,
            project_package=project_name_camel_case,
            module_name=project_name_snake_case,
        )

        shutil.move(tmpdir, project_module)
        return project_module, project_name
    except:
        try:
            dir_util.remove_tree(tmpdir)
        except:
            pass  # safe to ignore

        raise


def new_model(name, project_path, project_package, module_name=None):
    """
    Create a new model template under the project path

    :param name: model name
    :param project_path: path to the project directory
    :param project_package: package name of the project
    :param module_name: module name for the model. By default it is model name in snake case format
    """
    assert module_name, "module_name is missing"
    model_file = pathlib.Path(project_path) / 'models' / (module_name + ".py")

    if model_file.exists():
        raise ValueError(f'File {module_name}.py already exists')

    with open(model_file, "w") as f:
        f.write(_render_model_class(
            name,
            project_package,
        ))


def _render_init_graph_class(model_module, prefix):
    return """import h1st as h1
from .models.{model_module} import {prefix}Model


class {prefix}Graph(h1.Graph):
    def __init__(self):
        super().__init__()

        self.start()
        self.add({prefix}Model())
        self.end()
""".format(prefix=prefix, model_module=model_module)


def _render_schema_testcase(project_package, prefix):
    return """
from h1st.schema.testing import setup_schema_tests
from {project_package}.graph import {prefix}Graph


setup_schema_tests({prefix}Graph(), globals())
""".format(prefix=prefix, project_package=project_package)


def _render_model_class(name, base_package):
    return """import h1st as h1


class {name}(h1.Model):
    def get_data(self):
        # Implement code to retrieve your data here
        return dict()

    def prep_data(self, data):
        # Implement code to prepare your data here
        return data

    def train(self, prepared_data):
        # Implement your train method
        raise NotImplementedError()

    def evaluate(self, data):
        raise NotImplementedError()

    def predict(self, data):
        # Implement your predict function
        raise NotImplementedError()
""".format(name=name, base_package=base_package)


def _clean_name(name):
    # keep only valid character
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    snake_case = "".join(['_' + i.lower() if i.isupper() else i for i in name]).lstrip('_')
    camel_case = "".join([i.title() for i in snake_case.split("_")])
    return camel_case, snake_case
