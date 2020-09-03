import numpy as np
import pandas as pd
import lime
import lime.lime_tabular as lt
from h1st.core.trust.utils import get_model_name

class LIMEModelExplainer():
    def __init__(self, model, data, decision):
        self.model = model
        self.data = data
        self.model_type = get_model_name(self.model)
        self.feature_names = list(self.data["train_df"].columns)
        self.decision_input = decision[0]
        self.decision = decision[1]  
        self.lime_explainer()
        self.explain_decision()
    
    def explain_decision(self):
        self.explanation = self.explainer.explain_instance(            
            self.pred_input, self.model.predict,\
            #  num_features= self.top_n_features_to_explain
        )
    def lime_explainer(self):
        self.explainer = lt.LimeTabularExplainer(
            np.array(self.data["train_df"]),
            feature_names=self.feature_names,
            verbose=False,
            mode="regression"
        )

    