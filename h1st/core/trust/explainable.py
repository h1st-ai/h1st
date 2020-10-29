import logging
from .lime_model_explainer import LIMEModelExplainer
from .enums import Constituency, Aspect
from .explainer import Explainer


class Explainable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Explainable`, i.e., they can self-explain certain decisions they have made. For example,
    an `Explainable` `Model` should be able to provide a detailed explanation of a specific decision
    it made at some specified time or on a given set of inputs in the past.
    """
    def __get__(self, instance, owner):
        self.model_instance = instance
        self.model_instance.model_name = type(self.model_instance).__name__
        return self.__call__

    def __init__(self, function):
        self.model_function = function

    def __call__(self, *args, **kwargs):
        if isinstance(self.model_instance, Explainable):
            return self.model_instance._collect_explain_artifacts(
                self, *args, **kwargs)

    def _collect_explain_artifacts(self, explainable_decorator, *args,
                                   **kwargs):
        model_function_output = explainable_decorator.model_function(
            explainable_decorator.model_instance, *args, **kwargs)
        # change __model_describe_artifacts to __describe_artifacts
        if not hasattr(explainable_decorator.model_instance,
                       '_Explainable__explain_artifacts'):
            explainable_decorator.model_instance.__explain_artifacts = {}

        def collect(
                model_instance,
                model_function_name,
                model_function_output,
                *args,
        ):
            model_functions = {
                "load_data":
                explainable_decorator._collect_load_data_artifacts,
                "prep": explainable_decorator._collect_prep_artifacts,
                "train": explainable_decorator._collect_train_artifacts,
                "evaluate": explainable_decorator._collect_evaluate_artifacts,
            }
            return model_functions[model_function_name](
                model_instance,
                model_function_name,
                model_function_output,
                *args,
            )

        collect(self, explainable_decorator.model_function.__name__,
                model_function_output, *args)
        return model_function_output

    def explain(self,
                dataset_key=None,
                decision=None,
                constituent=Constituency.ANY,
                aspect=Aspect.ANY):
        """
        Returns an explanation for a decision made by the Model based on `Who's asking` and `why`.
            Parameters:
                dataset_key : The Dataset key in prepared data that maps to the dataset to be described
                decision : tuple : array-like input data of the decision to be explained, model decision
                constituent : Constituency: The `Constituency` asking for the explanation
                aspect : Aspect: The `Aspect` of the question (e.g., Accountable, Functional, Operational)
                
            Returns:
                out : Specific decision explanation (e.g., SHAP or LIME)
        """

        # self.__explain_artifacts['model_explainer']
        self._collect_decision_artifacts(decision)
        self.__explain_artifacts['model_explainer'] = LIMEModelExplainer(
            decision[0],
            self.__explain_artifacts[self.model_name]
            ['base_model'],  # to make explicit dataset_name & model_name are the same
            self.__explain_artifacts['prep']['function_output'][dataset_key])
        # self._generate_decision_report(dataset_key, decision, constituent,
        #                                aspect)
        return self.__explain_artifacts

    def _generate_decision_report(self, dataset_key, decision, constituent,
                                  aspect):
        pass

    def _collect_model_artifacts(self, model_instance, model_function_output):
        model_instance.__explain_artifacts[model_instance.model_name] = {
            "base_model": model_instance._base_model,
            "base_model_name": type(model_instance._base_model).__name__,
            "base_model_params": model_instance._base_model.get_params(),
            "base_model_metrics": model_instance.metrics
        }

    def _collect_dataset_artifacts(self, model_instance,
                                   model_function_output):
        model_instance.__explain_artifacts["dataset"] = {
            "name":
            model_instance.dataset_name,
            "description":
            model_instance.dataset_description,
            "label_column":
            model_instance.label_column,
            "feature_columns":
            set(list(model_function_output.columns)) -
            set(model_instance.label_column)
        }

    def _collect_load_data_artifacts(self, model_instance, model_function_name,
                                     model_function_output, *args):
        model_instance.__explain_artifacts[model_function_name] = {
            "function_input": args,
            "function_output": model_function_output
        }
        self._collect_dataset_artifacts(model_instance, model_function_output)

    def _collect_prep_artifacts(self, model_instance, model_function_name,
                                model_function_output, *args):
        print(model_function_name)
        model_instance.__explain_artifacts[model_function_name] = {
            "function_input": args,
            "function_output": model_function_output
        }
        logging.info("prep completed")

    def _collect_train_artifacts(self, model_instance, model_function_name,
                                 model_function_output, *args):
        model_instance.__explain_artifacts[model_function_name] = {
            "function_input": args,
            "function_output": model_function_output
        }
        logging.info("train completed")

    def _collect_evaluate_artifacts(self, model_instance, model_function_name,
                                    model_function_output, *args):
        model_instance.__explain_artifacts[model_function_name] = {
            "function_input": args,
            "function_output": model_function_output
        }
        self._collect_model_artifacts(model_instance, model_function_output)

    def _collect_decision_artifacts(self, decision):
        self.__explain_artifacts["decision"] = {
            "function_input": decision[0],
            "function_output": decision[1]
        }
