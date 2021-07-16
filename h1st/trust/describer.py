class Describer:
    """
    A Describer is one that stores all relevant details about the objects (e.g., `Models`, `Graphs`).
    This is important to have because if and when a constituent asks about the `Model` or `Graph`,
    the Describer will provide all pertenant details. For example, if a Regulator identifies that the model
    is indicating bias in its decision making, she may asks for details such as `when was the model trained',
    `by whom' and 'on what data was the model trained'
    """

    def __init__(self, h1stmodel):
        self.shap_describer = None
        self.data_description(h1stmodel)
        self.model_description(h1stmodel)
        
    def data_description(self, h1stmodel):
        self.h1stmodel = h1stmodel
        _dict = {}
        data = h1stmodel.prepared_data
        _dict["data_set_name"] = h1stmodel.dataset_name
        _dict["data_set_description"] = h1stmodel.dataset_description
        _dict["label_column"] = h1stmodel.label_column
        _dict["features"] = list(data["train_df"].columns)
        _dict["number_of_features"] = len(_dict["features"])
        _dict["number_of_rows"] = data["train_df"].shape[0]
        _dict["statistics"] = data["train_df"].describe()
        self.data_describer = _dict

    def model_description(self, h1stmodel):
        _dict = {}
        model = h1stmodel._native_model
        _dict["model_name"] = str(type(model).__name__)
        _dict["model_params"] = model.get_params()
        _dict["model_metrics"] = h1stmodel.metrics
        self.model_describer = _dict

    def generate_report(self, constituency, aspect):
        pass