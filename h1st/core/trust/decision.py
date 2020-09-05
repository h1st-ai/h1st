class Decision:
    """
    A Decision is one that stores all relevant details pertaining to the decision
    that was made by the Model or Graph, the dataset that was used and the Model
    or Graph that was used to make the decision. For example, `what data was used
    to train the model`, `how many features were used to train the model`
    and `tell me how does the model make decisions`
    """

    def __init__(self, h1stmodel):
        self.data_dict = {}
        self.model_dict = {}
        self.decision_dict = {}
        self.lime_explainer = {}
        self.data_description(h1stmodel)
        self.model_description(h1stmodel)
        self.decision_describer = self.decision_dict
        self.model_describer = self.model_dict
        self.decision_describer = self.data_dict

    def data_description(self, data):
        pass

    def model_description(self, model):
        pass

    def decision_description(self, decision):
        pass