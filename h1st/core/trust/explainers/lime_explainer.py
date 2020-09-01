import numpy as np
import pandas as pd
import lime
import lime.lime_tabular as lt


 
class LIMEExplainer():
    def __init__(self, model, data, predictions):
        super().__init__()
        self.model = model
        self.data = data
        self.model_type = str(type(self.model).__name__)
        self.features = list(self.data["train_df"].columns)
        self.predictions = predictions
        self.get_lime_explainer()
        self.plot_lime_explain()

    def _get_sample_lime_explain(self, idx):
        self.prediction = self.lime_explainer.explain_instance(
            self.data["train_df"].reset_index(drop=True).iloc[idx], self.model.predict
        )
        return self.prediction
 
    def get_lime_explainer(self):
        if self.model_type == "RandomForestRegressor":
            self.lime_explainer = lt.LimeTabularExplainer(
                np.array(self.data["train_df"]),
                feature_names=self.features,
                # class_names=['Label'],
                # categorical_features=,
                # There is no categorical features in this example, otherwise specify them.
                verbose=True,
                mode="regression",
            )
 
    def plot_lime_explain(self):
        for prediction, idx in self.predictions.items():
            self._get_sample_lime_explain(idx).show_in_notebook(
            show_table=True, show_all=True)
        
            