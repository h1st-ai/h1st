import pathlib
import tempfile
import shutil
import re
import os
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

        if not (path / "config.py").exists():
            raise ValueError('Please run this command in the package folder')

        model_path.mkdir(exist_ok=True)

        class_name, module_name = _clean_name(model_name)

        if not class_name.lower().endswith("model"):
            class_name = f"{class_name}Model"

        new_model(
            class_name,
            path,
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
        data_folder = tmppath / 'data'
        test_folder = tmppath / 'tests'

        # create all folders
        data_folder.mkdir(exist_ok=True)
        test_folder.mkdir(exist_ok=True)

        # create all empty files
        (tmppath / 'config.py').touch()
        (test_folder / '__init__.py').touch()
        (data_folder / '.gitkeep').touch()

        model_name = f"{class_prefix}Model"
        model_package = f"{project_name_snake_case}_model"

        graph_file = tmppath / f'{project_name_snake_case}_graph.py'
        with open(graph_file, "w") as f:
            f.write(_render_init_graph_class(class_prefix, model_package))

        service_file = tmppath / f'{project_name_snake_case}_service.py'
        with open(service_file, "w") as f:
            f.write(_render_init_service_class(class_prefix, model_package))

        with open(test_folder / "test_schema.py", "w") as f:
            f.write(_render_template('schema_testcase', {
                'GRAPH_PACKAGE': f'{project_name_snake_case}_graph',
                'GRAPH_CLASS': f'{class_prefix}Graph'
            }))

        with open(tmppath / 'config.py', 'w') as f:
            f.write(_render_template('config', {}))

        new_model(
            model_name,
            tmppath,
            model_file=f"{model_package}.py",
        )

        with open(tmppath / f"{project_name_snake_case}_notebook.ipynb", "w") as f:
            f.write(_render_template('notebook', {
                'MODEL_CLASS': model_name,
                'MODEL_PACKAGE': model_package,
            }))

        with open(test_folder / f'test_{model_package}.py', 'w') as f:
            f.write(_render_template('testcase', {
                'MODEL_CLASS': model_name,
                'MODEL_PACKAGE': model_package,
            }))


        with open(tmppath / 'run_tests.py', 'w') as f:
            f.write(_render_template('run_tests', {}))

        (tmppath / 'run_tests.py').chmod(0o777)

        shutil.move(tmpdir, project_module)
        return project_module, project_name
    except:
        try:
            dir_util.remove_tree(tmpdir)
        except:
            pass  # safe to ignore

        raise


def new_model(name, project_path, module_name=None, model_file=None):
    """
    Create a new model template under the project path

    :param name: model name
    :param project_path: path to the project directory
    :param module_name: module name for the model. By default it is model name in snake case format
    """
    if not model_file:
        assert module_name, "module_name is missing"
        model_file = pathlib.Path(project_path) / 'models' / (module_name + ".py")
    else:
        model_file = pathlib.Path(project_path) / model_file

    if model_file.exists():
        raise ValueError(f'File {model_file} already exists')

    with open(model_file, "w") as f:
        f.write(_render_template("model", {
            "MODEL_CLASS": name,
        }))


def _render_init_graph_class(prefix, model_package):
    return _render_template("graph", {
        "GRAPH_CLASS": f"{prefix}Graph",
        "MODEL_CLASS": f"{prefix}Model",
        "MODEL_PACKAGE": model_package
    })


def _render_init_service_class(prefix, model_package):
    return _render_template("service", {
        "SERVICE_CLASS": f"{prefix}Service",
        "GRAPH_CLASS": f"{prefix}Graph",
        "MODEL_PACKAGE": model_package
    })


def _render_notebook(package_name, model_name, model_file_name):
    subl = {
        'MODEL_NAME': model_name,
        'MODEL_FILE': model_file_name,
        'PACKAGE_NAME': package_name,
    }

    return _render_template('notebook', subl)


def _clean_name(name):
    # keep only valid character
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    snake_case = "".join(['_' + i.lower() if i.isupper() else i for i in name]).lstrip('_')
    snake_case = re.sub("_+", "_", snake_case)

    camel_case = "".join([i.title() for i in snake_case.split("_")])
    camel_case = camel_case.replace("H1St", "H1st")  # special treatment for the name

    return camel_case, snake_case


def _render_template(name, replaces):
    """
    Simple function to do template replacement. All variables are prefixed and suffixed
    with ``$$``, and then replace accordingly.
    """
    tpl = os.path.join(os.path.dirname(__file__), 'templates', f"{name}.txt")
    with open(tpl, 'r') as f:
        content = f.read()

    for k, v in replaces.items():
        content = content.replace(f"$${k}$$", v)

    return content
