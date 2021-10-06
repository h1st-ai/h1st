import abc
from typing import Any


class Node(abc.ABC):
    @abc.abstractmethod
    def execute(self, *previous_output: Any):
        pass
