import abc
from typing import Any


class Node(abc.ABC):
    __attributes: dict

    def __init__(self, **attr):
        self.__attributes = attr

    @abc.abstractmethod
    def execute(self, previous_output: Any = None):
        pass

    @property
    def attributes(self):
        return self.__attributes

    @property
    def name(self):
        return self.__attributes.get("name", "")
