class Explainer:
    """
    An Explainer is one that stores all relevant details about the explanation
    of a decision that was made by the Model or Graph. For example, details such as
    `what was the original decision`, `what were the key factors that led to that decision` and
    `what type of model was used to make the decision` etc.
    """
    def __init__(self, model, decision):
        self._decision_description(decision, model)

    @property
    def lime_explainer(self):
        return self._explainer

    @lime_explainer.setter
    def lime_explainer(self, value):
        self._explainer = value

    def decision_explainer(self, decision_input, model, train_data) -> None:
        """
        Implement logic to describe model output
        """
