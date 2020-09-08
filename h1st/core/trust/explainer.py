from .enums import Constituency, Aspect

class Explainer:
    """
    An Explainer is one that stores all relevant details about the explanation
    of a decision that was made by the Model or Graph. For example, details such as
    `what was the original decision`, `what were the key factors that led to that decision` and
    `what type of model was used to make the decision` etc.
    """
    def __init__(self, decision, h1stmodel):
        self.lime_explainer = None
        self.decision_description(h1stmodel, decision)

    def decision_description(self, decision, h1stmodel):
        _dict = {}
        model = h1stmodel.ml_model
        _dict["model_name"] = str(type(model).__name__)        
        _dict["data_set_name"] = h1stmodel.dataset_name
        _dict["data_set_description"] = h1stmodel.dataset_description
        _dict["label_column"] = h1stmodel.label_column
        _dict["decision_input"] = decision[0]
        _dict["decision"] = decision[1]
        self.decision_describer = _dict

    def generate_report(self, decision, constituent, aspect):               
        method_name = str(Constituency(constituent).name)
        aspect_name = str(Aspect(aspect).name)
        print('\n\t\t\tConstituent:{};  Aspect :{}\n'.format(method_name, aspect_name))
        method = getattr(self, method_name, lambda: "Invalid Constituent Method Name")
        return method()

    def DATA_SCIENTIST(self):
        print("\n\t\tDataset Details\n")
        print(self.decision_describer.items())
        print('\n\t\t Features responsibile for the Model making a Decision\n')
        self.lime_explainer.explanation.show_in_notebook(show_table=True, show_all=False)

    def REGULATOR(self):
        keys = ['model_name', 'data_set_name', 'data_set_description', 'label_column']
        for k,v in self.decision_describer.items():
            if k in keys:
                print('\n\t\t{}:{}'.format(k,v))
        print('\n\t\t Features responsibile for the Model making a Decision\n')
        self.lime_explainer.explanation.show_in_notebook(show_table=True, show_all=False)
