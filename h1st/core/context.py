import sys
import os
import pathlib
import logging

from h1st.model.repository.model_repository import ModelRepository

class Context:
    def __init__(self):
        pass

    @classmethod
    def init_model_repo(cls, repo_path):
        if not hasattr(ModelRepository, 'MODEL_REPO'):
            setattr(ModelRepository, 'MODEL_REPO', ModelRepository(storage=repo_path))


def init(address=None, MODEL_REPO_PATH=None):
    # TODO: notebook or script only?
    module_path, parent_path = discover_h1st_project()

    # so that project package can be importable immediately
    if parent_path and parent_path not in sys.path:
        sys.path.append(parent_path)

    if MODEL_REPO_PATH:
        Context.init_model_repo(MODEL_REPO_PATH)


def discover_h1st_project(cwd=None) -> tuple:
    # add current dir to cwd
    sys.path.append(os.getcwd())

    cur = pathlib.Path(cwd or os.getcwd())
    last_is_module = None

    module_path = None
    parent_path = None

    while cur != cur.parent:
        # detect the root of the H1ST project structure
        # some project does not have graph.py yet, so we only look for config file for now
        if (cur / "config.py").exists():
            last_is_module = True
            module_path = str(cur)
        elif last_is_module:
            parent_path = str(cur)
            break

        cur = cur.parent

    return module_path, parent_path


_stream_handler = None
def setup_logger():
    global _stream_handler

    name = __name__.split(".")[0]
    logger = logging.getLogger(name)

    if not _stream_handler:
        _stream_handler = logging.StreamHandler()
        _stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))

        logger.addHandler(_stream_handler)

    logger.setLevel(logging.INFO)
