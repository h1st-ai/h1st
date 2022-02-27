from abc import ABC
from typing import Any, Dict
from .serdes import JobLibSerDes


class Serializable(ABC):
    def to_json(self) -> str:
        # TODO: implement
        pass
    
    @classmethod
    def from_json(cls, data: str) -> 'Serializable':
        # TODO: implement
        pass

    def to_dict(self) -> Dict:
        # TODO: implement
        pass

    @classmethod
    def from_dict(cls, data: Dict) -> 'Serializable':
        # TODO: implement
        pass

    def to_file(self) -> str:
        """
        :returns: filename containing serialized object
        """
        return JobLibSerDes.do_serialize(self)

    @classmethod
    def from_file(cls, file_name: str) -> 'Serializable':
        """
        :param file_name: name of file containing serialized object
        :returns: deserialized object
        """
        return JobLibSerDes.do_deserialize(file_name)