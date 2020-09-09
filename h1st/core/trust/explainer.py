class Explainer:
    """
    An Explainer is one that stores all relevant details about the explanation
    of a decision that was made by the Model or Graph. For example, details such as
    `what was the original decision`, `what were the key factors that led to that decision` and
    `what type of model was used to make the decision` etc.
    """
    def __init__(self, h1stmodel, decision):
        self.lime_explainer = None
        self.decision_description(decision, h1stmodel)

    def decision_description(self, decision, h1stmodel):
        _dict = {}
        model = h1stmodel._native_model
        _dict["model_name"] = str(type(model).__name__)        
        _dict["data_set_name"] = h1stmodel.dataset_name
        _dict["data_set_description"] = h1stmodel.dataset_description
        _dict["label_column"] = h1stmodel.label_column
        _dict["decision_input"] = decision[0]
        _dict["decision"] = decision[1]
        self.decision_describer = _dict

    def generate_report(self, decision, constituency, aspect):
        pass