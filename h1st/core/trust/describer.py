# Similarly for explainer and lime explainer
class Describer:
    """
    A Describer is one that stores all relevant details about the objects (e.g., `Models`, `Graphs`).
    This is important to have because if and when a constituent asks about the `Model` or `Graph`,
    the Describer will provide all pertenant details. For example, if a Regulator identifies that the model
    is indicating bias in its decision making, she may asks for details such as `when was the model trained',
    `by whom' and 'on what data was the model trained'
    """
    @property
    def shap_describer(self):
        return self._describer

    @shap_describer.setter
    def shap_describer(self, value):
        self._describer = value

    def model_describer(self, model, data_to_describe) -> None:
        """
        Implement logic to describe model output
        """