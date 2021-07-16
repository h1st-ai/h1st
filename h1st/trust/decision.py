class Decision:
    """
    A Decision is one that stores all relevant details pertaining to the decision
    that was made by the Model or Graph, the dataset that was used and the Model
    or Graph that was used to make the decision. For example, `what data was used
    to train the model`, `how many features were used to train the model`
    and `tell me how does the model make decisions`
    """

    def data_description(self, data):
        pass

    def model_description(self, model):
        pass

    def decision_explainer(self, decision):
        pass
