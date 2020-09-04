import numpy as np
import pandas as pd
import lime
import lime.lime_tabular as lt

class LIMEModelExplainer():
    def __init__(self, decision, model, data):
        self.model = model
        self.data = data
        self.feature_names = list(self.data["train_df"].columns)
        self.decision_input = decision
        self.lime_explainer()
        self.explain_decision()
    
    def explain_decision(self):
        self.explanation = self.explainer.explain_instance(            
            self.decision_input, self.model.predict,
        )
    def lime_explainer(self):
        self.explainer = lt.LimeTabularExplainer(
            np.array(self.data["train_df"]),
            feature_names=self.feature_names,
            verbose=False,
            mode="regression"
        )

    