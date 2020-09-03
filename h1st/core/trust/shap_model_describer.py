import numpy as np
import matplotlib.pyplot as plt
import shap
import pandas as pd
from h1st.core.trust.utils import get_model_name

class SHAPModelDescriber():
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.model_type = get_model_name(self.model)       
        self.get_shap_describer()
        self.get_shap_values() 

    def get_shap_describer(self):
        self.shap_describer = shap.TreeExplainer(self.model)

    def get_shap_values(self):
        self.shap_values = self.shap_describer.shap_values(
            self.data["train_df"].reset_index(drop=True)
        )

    