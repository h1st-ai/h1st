from collections import defaultdict
import logging
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
    def __get__(self, instance, owner):
        self.model_instance = instance
        return self.__call__

    def __init__(self, function):
        self.model_function = function

    def __call__(self, *args, **kwargs):
        if isinstance(self.model_instance, Describable):
            return self.model_instance._collect_describe_artifacts(
                self, *args, **kwargs)

    def _collect_describe_artifacts(self, describable_decorator, *args,
                                    **kwargs):
        model_function_output = describable_decorator.model_function(
            describable_decorator.model_instance, *args, **kwargs)
        # change __model_describe_artifacts to __describe_artifacts
        if not hasattr(describable_decorator.model_instance,
                       '_Describable__describe_artifacts'):
            describable_decorator.model_instance.__describe_artifacts = {}

        def collect(
                model_instance,
                model_function_name,
                model_function_output,
                *args,
        ):
            model_functions = {
                "prep": describable_decorator._collect_prep_artifacts,
                "train": describable_decorator._collect_train_artifacts,
            }
            return model_functions[model_function_name](
                model_instance,
                model_function_name,
                model_function_output,
                *args,
            )

        collect(self, describable_decorator.model_function.__name__,
                model_function_output, *args)
        return model_function_output

    @property
    def description(self):
        return getattr(self, "__description", {})

    @description.setter
    def description(self, value):
        setattr(self, "__description", value)

    def describe(self,
                 dataset_key=None,
                 constituency=Constituency.ANY,
                 aspect=Aspect.ANY):
        """
        Returns a description of the model's behavior and properties based on `Who's asking` for `what`.

            Parameters:
                dataset_key : The Dataset key in prepared data that maps to the dataset to be described
                constituent : Constituency: The Constituency asking for the explanation `Who`
                aspect : The Aspect of the question. `What`

            Returns:
                out : Description of Model's behavior and properties
        """
        self.__describe_artifacts['shap_model_describer'] = SHAPModelDescriber(
            self.__describe_artifacts['train']['base_model'],
            self.__describe_artifacts['prep']['function_output'][dataset_key])
        # describer.generate_report(constituency, aspect)
        return self.__describe_artifacts

    def _collect_prep_artifacts(self, model_instance, model_function_name,
                                model_function_output, *args):
        model_instance.__describe_artifacts[model_function_name] = {
            "function_input": args,
            "function_output": model_function_output,
            ## Move line below to dataset_key rather than model_function
            "dataset_name": model_instance.dataset_name,
            "dataset_description": model_instance.dataset_description,
            "label_column": model_instance.label_column,
            "features": list(model_function_output["train_df"].columns),
            "dataset_shape": model_function_output["train_df"].shape,
            "dataset_statistics": model_function_output["train_df"].describe()
        }
        logging.info("prep completed")

    def _collect_train_artifacts(self, model_instance, model_function_name,
                                 model_function_output, *args):
        model_instance.__describe_artifacts[model_function_name] = {
            "base_model": model_instance._base_model,
            "function_input": args,
            "function_output": model_function_output,
            "base_model_name": type(model_instance._base_model).__name__,
            "base_model_params": model_instance._base_model.get_params(),
            "model_metrics": model_instance.metrics
        }
        logging.info("train completed")
