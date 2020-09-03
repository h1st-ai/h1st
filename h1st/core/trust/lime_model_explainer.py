import numpy as np
#import lime.lime_tabular as lt
 
class LIMEModelExplainer():
    def __init__(self, model, data, predictions, plot, verbose=0):
        super().__init__()
        self.plot=plot    
        self.model=model
        self.data=data
        self.model_type=get_model_name(self.model)
        self.features = list(self.data["train_df"].columns)
        self.predictions = predictions
        self.get_lime_explainer()
        self.get_decision_lime_explainer()
        
          

    def return_lime_predictions(self):
        return {"lime_predictions":self.decision_explainer.as_list()}
    
    def generate_plots(self):
        self.decision_explainer.show_in_notebook(
            show_table=True, show_all=True)

    def get_decision_lime_explainer(self):
        for prediction, idx in self.predictions.items():            
            self.decision_explainer = self.lime_explainer.explain_instance(
                self.data["train_df"].reset_index(drop=True).iloc[idx], self.model.predict
            )
            if self.plot:
                self.generate_plots() 

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
 
   
        
            