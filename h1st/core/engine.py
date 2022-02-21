import abc
from typing import Any

from h1st.core.graph import GraphInfo


class ExecutionEngine(abc.ABC):
    @abc.abstractmethod
    def execute(self, graph: GraphInfo, data: Any):
        pass
