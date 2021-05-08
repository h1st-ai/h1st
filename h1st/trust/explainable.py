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

    def explain(self, decision=None, constituent=Constituency.ANY, aspect=Aspect.ANY):
        """
        Returns an explanation for a decision made by the Model based on `Who's asking` and `why`.

            Parameters:
                constituent : Constituency: The `Constituency` asking for the explanation
                aspect : Aspect: The `Aspect` of the question (e.g., Accountable, Functional, Operational)
                decision : array-like: the input data of the decision to be explained

            Returns:
                out : Specific decision explanation (e.g., SHAP or LIME)
        """
        explainer = Explainer(self, decision)
        explainer.lime_explainer = LIMEModelExplainer(
            decision, self._native_model, self.prepared_data
        )
        explainer.generate_report(decision, constituent, aspect)
        return explainer
