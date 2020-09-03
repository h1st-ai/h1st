from .lime_model_explainer import LIMEModelExplainer
from .enums import Constituency, Aspect

class Explainable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Explainable`, i.e., they can self-explain certain decisions they have made. For example,
    an `Explainable` `Model` should be able to provide a detailed explanation of a specific decision
    it made at some specified time or on a given set of inputs in the past.
    """

    def explain(self, constituent=Constituency.ANY, aspect=Aspect.ANY, decision=None):
        '''
        Returns an explanation for a decision made by the Model based on `Who's asking` and `why`.

            Parameters:
                constituent : Constituency: The `Constituency` asking for the explanation
                aspect : Aspect: The `Aspect` of the question (e.g., Accountable, Functional, Operational)
                decision : array-like: the input data of the decision to be explained

            Returns:
                out : Specific decision explanation (e.g., SHAP or LIME)               
        '''
        e = LIMEModelExplainer(self.model, self.prepared_data, decision)
        return {'lime_explainer': e}





# self.verbose = verbose   
#         self.model = model
#         self.data = data
#         self.model_type = get_model_name(self.model)
#         self.feature_names = list(self.data["train_df"].columns)
#         self.metrics = metrics
#         self.constituent_name = constituent.upper()
#         self.cosntituent_number = get_cosntituent_number(self.constituent_name)
#         self.top_n_features_to_explain = get_top_n_features_to_explain_constituent(self.cosntituent_number)
#         self.pred_input = decision[0]
#         self.label = decision[1]
#         self.aspect = aspect    
#         self.lime_explainer()
#         self.explain_decision()
#         if verbose:
#             self.constituent_explanation(self.cosntituent_number)


#     def constituent_explanation(self, argument):
#         def number_to_constituent_function_name(argument):        
#             switcher = {
#                 10: 'data_scientist_view',
#                 60: 'regulator_view'
#             }
#             return str(switcher.get(argument, lambda: "Invalid Constituent Number"))
#         method_name = number_to_constituent_function_name(argument)
#         method = getattr(self, method_name, lambda: "Invalid Constituent Method Name")
#         # Call the method as we return it
#         return method()
 
#     def data_scientist_view(self):
#         print('\n')
#         print("\t\t\t\t\tData Scientist View!".upper())
#         print('\n')
#         print('\t\t\tDecision Explanation')
#         print('\t\t\t\tAcual Rating: {:0.2f} Model Rating: {:0.2f} LIME Local Rating: {:0.2f}'.format(self.label, self.decision_explained.predicted_value,list(self.decision_explained.local_pred)[0]))
#         print('\n')
#         print('\t\t\t\tTop {} Feature Importance '.format(self.top_n_features_to_explain))
#         self.decision_explained.show_in_notebook(show_all=False,show_table=True)
 
#     def regulator_view(self):
#         print('\n')
#         print("\t\t\t\t\tRegulator View!".upper())
#         print('\n')
#         print('\t\t\tDecision Explanation')
#         print('\t\t\t\tAcual Rating: {:0.2f} Model Rating: {:0.2f}'.format(self.label, self.decision_explained.predicted_value))
#         print('\n')
#         print('\t\t\t\t\tTop {} Feature Importance '.format(self.top_n_features_to_explain))
#         self.decision_explained.show_in_notebook(show_all=False,show_table=False)


# self.feature_names = list(self.data["train_df"].columns)
# def get_ordered_important_features(self):
#         vals= np.abs(self.shap_values).mean(0)        
#         feature_importance = pd.DataFrame(list(zip(self.feature_names,vals)),columns=['column_name','feature_importance_vals'])
#         return feature_importance.sort_values(by=['feature_importance_vals'],ascending=False)    

#     def constituent_explanation(self, argument):
#         def number_to_constituent_function_name(argument):        
#             switcher = {
#                 10: 'data_scientist_view',
#                 60: 'regulator_view'
#             }
#             return str(switcher.get(argument, lambda: "Invalid Constituent Number"))
#         method_name = number_to_constituent_function_name(argument)
#         method = getattr(self, method_name, lambda: "Invalid Constituent Method Name")
#         # Call the method as we return it
#         return method()

#     def data_scientist_view(self):
#         print('\n')
#         print("\t\t\t\t\tData Scientist View!".upper())
#         print('\n')
#         print('\t\t\tTraining Data'.format())
#         rows, columns = self.data['train_df'].shape[0], self.data['train_df'].shape[1]
#         print("\t\t\t\tNumber of row:{} ; features:{}".format(rows, columns))
#         # print('         Features: {}'.format(self.feature_names))
#         print('\n')
#         print('\t\t\tModel Details   ')
#         print('\t\t\t\tModel Type:{}'.format(self.model_type))
#         print('\t\t\t\tModel Metrics:{}'.format(self.metrics))
#         print('\n')
        
#         print('The plot below shows SHAP values of every feature for every sample.')
#         print('The SHAP values show the distribution of the impacts each feature has on the model output.')
#         print('The color represents the feature value (red high, blue low).')
#         print('For example, high alcohol increases the predicted wine quality.')        
#         print('\n')
#         shap.summary_plot(self.shap_values, self.data["train_df"])
#         print('\n')
#         print('Dependence plots for the 3 most Impactful Features') 
#         tmp_df = self.get_ordered_important_features()        
#         for column in list(tmp_df.column_name.values)[:3]:
#             shap.dependence_plot(column, self.shap_values, self.data["train_df"])

#     def regulator_view(self):
#         print('\n')
#         print("\t\t\t\t\tData Scientist View!".upper())
#         print('\n')
#         print('\t\t\tTraining Data'.format())
#         rows, columns = self.data['train_df'].shape[0], self.data['train_df'].shape[1]
#         print("\t\t\tNumber of row:{} ; features:{}".format(rows, columns))
#         # print('         Features: {}'.format(self.feature_names))
#         print('\n')
#         print('\t\t\tModel Details')
#         print('\t\t\t\tModel Type:{}'.format(self.model_type))
#         print('\t\t\t\tModel Metrics:{}'.format(self.metrics))
#         print('\n')
        
#         print('The plot below shows SHAP values of every feature for every sample.')
#         print('The SHAP values show the distribution of the impacts each feature has on the model output.')
#         print('The color represents the feature value (red high, blue low).')
#         print('For example, high alcohol increases the predicted wine quality.')        
#         print('\n')
#         shap.summary_plot(self.shap_values, self.data["train_df"])
#         print('\n')

    
