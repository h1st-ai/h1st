import abc

from h1st.core.graph import GraphInfo


class ExecutionEngine(abc.ABC):
    @abc.abstractmethod
    def execute(self, graph: GraphInfo):
        pass
