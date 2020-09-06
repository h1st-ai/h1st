from typing import Any
import h1st as h1

class MLModel(h1.Model):

    @property
    def base_model(self) -> Any:
        return getattr(self, "__base_model", None)

    @base_model.setter
    def base_model(self, value):
        setattr(self, "__base_model", value)
