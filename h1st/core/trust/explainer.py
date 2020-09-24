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

    def _decision_description(self, decision, model):
        _dict = {}
        _native_model = model._native_model
        _dict["model_name"] = str(type(_native_model).__name__)        
        _dict["data_set_name"] = model.dataset_name
        _dict["data_set_description"] = model.dataset_description
        _dict["label_column"] = model.label_column
        _dict["decision_input"] = decision[0]
        _dict["decision"] = decision[1]
        self.decision_describer = _dict

    def generate_report(self, decision, constituency, aspect):
        pass