import numpy as np
import matplotlib.pyplot as plt
import shap
import pandas as pd


class SHAPModelDescriber:
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.get_shap_describer()
        self.get_shap_values()

    def get_shap_describer(self):
        self.shap_describer = shap.TreeExplainer(self.model)

    def get_shap_values(self):
        self.shap_values = self.shap_describer.shap_values(
            self.data["train_df"], check_additivity=False
        )
