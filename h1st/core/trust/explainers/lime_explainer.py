import numpy as np
import pandas as pd
import lime
import lime.lime_tabular as lt
from h1st.core.trust.explainers.utils import get_model_name, get_top_n_features_to_explain_constituent, get_cosntituent_number

 
class LIMEExplainer():
    def __init__(self, model, data, metrics, decision, constituent, aspect, verbose=True):
        super().__init__()
        self.verbose = verbose   
        self.model = model
        self.data = data
        self.model_type = get_model_name(self.model)
        self.feature_names = list(self.data["train_df"].columns)
        self.metrics = metrics
        self.constituent_name = constituent.upper()
        self.cosntituent_number = get_cosntituent_number(self.constituent_name)
        self.top_n_features_to_explain = get_top_n_features_to_explain_constituent(self.cosntituent_number)
        self.pred_input = decision[0]
        self.label = decision[1]
        self.aspect = aspect    
        self.lime_explainer()
        self.explain_decision()
        if verbose:
            self.constituent_explanation(self.cosntituent_number)
          

    def return_lime_predictions(self):
        return {"lime_predictions":self.decision_explained.as_list()}
    
    def generate_plots(self):
        self.decision_explained.show_in_notebook(show_all=False,show_table=True)

    def explain_decision(self):
        self.decision_explained = self.explainer.explain_instance(            
            self.pred_input, self.model.predict,\
             num_features= self.top_n_features_to_explain
        )

    def lime_explainer(self):
        if self.model_type == "RandomForestRegressor":
            self.explainer = lt.LimeTabularExplainer(
                np.array(self.data["train_df"]),
                feature_names = self.feature_names,
                verbose=False,
                mode="regression",
            )

    def constituent_explanation(self, argument):
        def number_to_constituent_function_name(argument):        
            switcher = {
                10: 'data_scientist_view',
                60: 'regulator_view'
            }
            return str(switcher.get(argument, lambda: "Invalid Constituent Number"))
        method_name = number_to_constituent_function_name(argument)
        method = getattr(self, method_name, lambda: "Invalid Constituent Method Name")
        # Call the method as we return it
        return method()
 
    def data_scientist_view(self):
        print('\n')
        print("\t\t\t\t\tData Scientist View!".upper())
        print('\n')
        print('\t\t\tDecision Explanation')
        print('\t\t\t\tAcual Rating: {:0.2f} Model Rating: {:0.2f} LIME Local Rating: {:0.2f}'.format(self.label, self.decision_explained.predicted_value,list(self.decision_explained.local_pred)[0]))
        print('\n')
        print('\t\t\t\tTop {} Feature Importance '.format(self.top_n_features_to_explain))
        self.decision_explained.show_in_notebook(show_all=False,show_table=True)
 
    def regulator_view(self):
        print('\n')
        print("\t\t\t\t\tRegulator View!".upper())
        print('\n')
        print('\t\t\tDecision Explanation')
        print('\t\t\t\tAcual Rating: {:0.2f} Model Rating: {:0.2f}'.format(self.label, self.decision_explained.predicted_value))
        print('\n')
        print('\t\t\t\t\tTop {} Feature Importance '.format(self.top_n_features_to_explain))
        self.decision_explained.show_in_notebook(show_all=False,show_table=False)