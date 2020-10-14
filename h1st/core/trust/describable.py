from collections import defaultdict
import weakref
from inspect import signature
from .shap_model_describer import SHAPModelDescriber
from .enums import Constituency, Aspect
from .describer import Describer
from .auditable import Auditable


class Describable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Describable, i.e., they can self-describe their properties and behaviors. For example,
    a `Describable` `Model` should be able to report the data that was used to train it, provide an
    importance-ranked list of its input features on a global basis, etc.
    """
    _instances = set()

    def __get__(self, instance, owner):
        self.model_instance = instance
        return self.__call__

    def __init__(self, function):
        self.model_function = function

    def __call__(self, *args, **kwargs):
        if isinstance(self.model_instance, Describable):
            return self.model_instance._collect_model_artifacts(
                self, *args, **kwargs)

    def _collect_model_artifacts(self, Describable, *args, **kwargs):
        model_function_output = Describable.model_function(
            Describable.model_instance, *args, **kwargs)
        if not hasattr(Describable.model_instance,
                       '_Describable__model_artifacts'):
            Describable.model_instance.__model_artifacts = defaultdict(dict)

        def collect(
                model_instance,
                model_function,
                model_function_output,
                *args,
        ):
            model_functions = {
                "prep": Describable._collect_prep,
                "train": Describable._collect_train,
            }
            return model_functions[model_function](
                model_instance,
                model_function,
                model_function_output,
                *args,
            )

        # Describable.instance.__model_artifacts[str(
        #     Describable.function.__name__)] = [args, function_output]
        # print(Describable.function.__name__)
        collect(self, Describable.model_function.__name__,
                model_function_output, *args)
        return model_function_output

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
        describer.shap_describer = SHAPModelDescriber(
            self.__model_artifacts['_build_base_model'],
            self.__model_artifacts['prep'])
        # describer.generate_report(constituency, aspect)
        return describer

    def _collect_prep(self, model_instance, model_function,
                      model_function_output, *args):
        model_instance.__model_artifacts[str(model_function)] = {
            "function_input": args,
            "function_output": model_function_output
        }
        print("prep completed")

    def _collect_train(self, model_instance, model_function,
                       model_function_output, *args):
        model_instance.__model_artifacts[str(model_function)] = {
            "base_model": model_instance._base_model,
            "function_input": args,
            "function_output": model_function_output
        }
        print("train completed")
