from .shap_model_describer import SHAPModelDescriber   # TODO: fix
from .enums import Constituency, Aspect
from .describer import Describer


class Describable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Describable, i.e., they can self-describe their properties and behaviors. For example,
    a `Describable` `Model` should be able to report the data that was used to train it, provide an
    importance-ranked list of its input features on a global basis, etc.
    """

    @property
    def description(self):
        return getattr(self, "__description", {})

    @description.setter
    def description(self, value):
        setattr(self, "__description", value)

    def describe(self, constituency=Constituency.ANY, aspect=Aspect.ANY):
        """
        Returns a description of the model's behavior and properties based on `Who's asking` for `what`.

            Parameters:
                constituent : Constituency: The Constituency asking for the explanation `Who`
                aspect : The Aspect of the question. `What`

            Returns:
                out : Description of Model's behavior and properties
        """
        describer = Describer(self)
        describer.shap_describer = SHAPModelDescriber(self._native_model, self.prepared_data)
        describer.generate_report(constituency, aspect)
        return describer
