from h1st.core.model import Model

class Describer:
    """
    A Describer is one that stores all relevant details about the objects (e.g., `Models`, `Graphs`).
    This is important to have because if and when a constituent asks about the `Model` or `Graph`,
    the Describer will provide all pertenant details. For example, if a Regulator identifies that the model
    is indicating bias in its decision making, she may asks for details such as `when was the model trained',
    `by whom' and 'on what data was the model trained'
    """

    def __init__(self, model):
        self._data_description(model)
        self._model_description(model)

    @property
    def shap_describer(self):
        return self._describer

    @shap_describer.setter
    def shap_describer(self, value):   
        self._describer = value
        
    def _data_description(self, model):
        self.model = model
        _dict = {}
        data = model.prepared_data
        _dict["data_set_name"] = model.dataset_name
        _dict["data_set_description"] = model.dataset_description
        _dict["label_column"] = model.label_column
        _dict["features"] = list(data["train_df"].columns)
        _dict["number_of_features"] = len(_dict["features"])
        _dict["number_of_rows"] = data["train_df"].shape[0]
        _dict["statistics"] = data["train_df"].describe()
        self.data_describer = _dict

    def _model_description(self, model):
        _dict = {}
        _native_model = model._native_model
        _dict["model_name"] = str(type(_native_model).__name__)
        _dict["model_params"] = _native_model.get_params()
        _dict["model_metrics"] = model.metrics
        self.model_describer = _dict

    def generate_report(self, constituency, aspect):
        pass