class Describer:
    """
    A Describer is one that stores all relevant details about the objects (e.g., `Models`, `Graphs`).
    This is important to have because if and when a constituent asks about the `Model` or `Graph`,
    the Describer will provide all pertenant details. For example, if a Regulator identifies that the model
    is indicating bias in its decision making, she may asks for details such as `when was the model trained',
    `by whom' and 'on what data was the model trained'
    """

    def __init__(self, h1stmodel):
        self.data_dict = {}
        self.model_dict = {}
        self.shap_describer = {}
        self.data_description(h1stmodel)
        self.model_description(h1stmodel)
        self.data_describer = self.data_dict
        self.model_describer = self.model_dict

    def data_description(self, h1stmodel):
        data = h1stmodel.prepared_data
        self.data_dict["data_set_name"] = h1stmodel.dataset_name
        self.data_dict["data_set_description"] = h1stmodel.dataset_description
        self.data_dict["label_column"] = h1stmodel.label_column
        self.data_dict["features"] = list(data["train_df"].columns)
        self.data_dict["number_of_features"] = len(self.data_dict["features"])
        self.data_dict["number_of_rows"] = data["train_df"].shape[0]
        self.data_dict["statistics"] = data["train_df"].describe()

    def model_description(self, h1stmodel):
        model = h1stmodel.model
        self.model_dict["model_name"] = str(type(model).__name__)
        self.model_dict["model_params"] = model.get_params()
        self.model_dict["model_metrics"] = h1stmodel.metrics
