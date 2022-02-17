from typing import Any
from abc import ABC


class Modelable(ABC):
    """
    Base class for all classes that are operated-upon by Modeler.
    """
    pass


class MLModelable(Modelable):
    """
    Base class for all classes that are operated-upon by MLModeler.
    """

    @property
    def base_model(self) -> Any:
        return getattr(self, "__base_model", None)

    @base_model.setter
    def base_model(self, value):
        setattr(self, "__base_model", value)