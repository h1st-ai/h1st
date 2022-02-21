import os
from typing import Any

from h1st.core.engine import ExecutionEngine
from h1st.core.graph import GraphInfo
from importlib import import_module


class ExecutionManager(object):

    @staticmethod
    def get_engine(engine_name: str) -> ExecutionEngine:
        try:
            module_path, class_name = engine_name.rsplit('.', 1)
            module = import_module(module_path)
            class_ = getattr(module, class_name)
            return class_()
        except (ImportError, AttributeError):
            raise ImportError(engine_name)

    @staticmethod
    def execute_with_engine(graph: GraphInfo, engine_class: str = None, data: Any = None):
        if engine_class is None:
            engine_name = os.environ["H1ST_ENGINE"]
        else:
            engine_name = engine_class
        engine = ExecutionManager.get_engine(engine_name)
        return engine.execute(graph, data)
