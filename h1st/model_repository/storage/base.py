from typing import Union, Any, NoReturn
from abc import ABC, abstractmethod


class Storage(ABC):
    """
    Base class for storage
    """
    @abstractmethod
    def get_obj(self, name: str) -> Any:
        ...

    @abstractmethod
    def set_obj(self, name: str, value: Any) -> NoReturn:
        ...

    @abstractmethod
    def get_bytes(self, name: str) -> bytes:
        ...

    @abstractmethod
    def set_bytes(self, name: str, value: bytes) -> NoReturn:
        ...

    @abstractmethod
    def exists(self, name: str) -> bool:
        ...

    @abstractmethod
    def delete(self, name: str) -> Any:
        ...

    def delete_namespace(self, namespace: str):
        raise NotImplementedError()

    def list_keys(self, namespace: str) -> list:
        raise NotImplementedError()
