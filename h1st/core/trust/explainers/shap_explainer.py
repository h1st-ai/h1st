import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt



class SHAPExplainer():
    def __init__(self, model, data):
        super().__init__()
        self.model = model
        self.data = data         
        self.model_type = str(type(self.model).__name__)
        self.get_shap_explainer()
        self.get_shap_values()        
        self.generate_plots()
        
       
 
    def _shap_local_plot(self, j):
        explainer_model = shap.TreeExplainer(self.model)
        shap_values_model = explainer_model.shap_values(self.samples)
        print(
            explainer_model.expected_value, shap_values_model[j], self.samples.iloc[[j]]
        )
        p = shap.force_plot(
            explainer_model.expected_value,
            shap_values_model[j],
            self.samples.iloc[[j]],
        )
        return p
 
    def _random_sample_generator(self):
        val_df = self.data["val_df"].copy()
        val_df.loc[:, "predict"] = np.round(self.model.predict(val_df), 2)
        random_picks = np.arange(1, val_df.shape[0], 50)
        return val_df.iloc[random_picks]

    def get_shap_explainer(self):
        if self.model_type == "RandomForestRegressor":
            self.shap_explainer = shap.TreeExplainer(self.model)

    def get_shap_values(self):
        self.shap_values = self.shap_explainer.shap_values(
            self.data["train_df"].reset_index(drop=True)
        )

    def generate_plots(self):
        shap.initjs()
        df = self.data["train_df"].reset_index(drop=True)
        shap.summary_plot(self.shap_values, self.data["train_df"])       
        shap.force_plot(self.shap_explainer.expected_value, self.shap_values, df)

