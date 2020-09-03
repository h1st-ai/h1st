import numpy as np
import matplotlib.pyplot as plt
from h1st.core.trust.explainers.utils import get_model_name
from h1st.core.trust.explainers.utils import get_model_name, get_top_n_features_to_explain_constituent, get_cosntituent_number



class SHAPModelDescriber():
    def __init__(self, model, data, metrics, constituent, aspect, verbose=True):
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
        self.aspect = aspect
        self.get_shap_explainer()
        self.get_shap_values()
        self.plot = plot
        if plot:
            self.generate_plots()

    def return_shap_values(self):
        return {'shap_values':self.shap_values}

    def _shap_local_plot(self, j):
        explainer_model = shap.TreeExplainer(self.model)
        shap_values_model = explainer_model.shap_values(self.samples)

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

    def get_ordered_important_features(self):
        vals= np.abs(self.shap_values).mean(0)        
        feature_importance = pd.DataFrame(list(zip(self.feature_names,vals)),columns=['column_name','feature_importance_vals'])
        return feature_importance.sort_values(by=['feature_importance_vals'],ascending=False)    

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
        print('\t\t\tTraining Data'.format())
        rows, columns = self.data['train_df'].shape[0], self.data['train_df'].shape[1]
        print("\t\t\t\tNumber of row:{} ; features:{}".format(rows, columns))
        # print('         Features: {}'.format(self.feature_names))
        print('\n')
        print('\t\t\tModel Details   ')
        print('\t\t\t\tModel Type:{}'.format(self.model_type))
        print('\t\t\t\tModel Metrics:{}'.format(self.metrics))
        print('\n')
        
        print('The plot below shows SHAP values of every feature for every sample.')
        print('The SHAP values show the distribution of the impacts each feature has on the model output.')
        print('The color represents the feature value (red high, blue low).')
        print('For example, high alcohol increases the predicted wine quality.')        
        print('\n')
        shap.summary_plot(self.shap_values, self.data["train_df"])
        print('\n')
        print('Dependence plots for the 3 most Impactful Features') 
        tmp_df = self.get_ordered_important_features()        
        for column in list(tmp_df.column_name.values)[:3]:
            shap.dependence_plot(column, self.shap_values, self.data["train_df"])

    def regulator_view(self):
        print('\n')
        print("\t\t\t\t\tData Scientist View!".upper())
        print('\n')
        print('\t\t\tTraining Data'.format())
        rows, columns = self.data['train_df'].shape[0], self.data['train_df'].shape[1]
        print("\t\t\tNumber of row:{} ; features:{}".format(rows, columns))
        # print('         Features: {}'.format(self.feature_names))
        print('\n')
        print('\t\t\tModel Details')
        print('\t\t\t\tModel Type:{}'.format(self.model_type))
        print('\t\t\t\tModel Metrics:{}'.format(self.metrics))
        print('\n')
        
        print('The plot below shows SHAP values of every feature for every sample.')
        print('The SHAP values show the distribution of the impacts each feature has on the model output.')
        print('The color represents the feature value (red high, blue low).')
        print('For example, high alcohol increases the predicted wine quality.')        
        print('\n')
        shap.summary_plot(self.shap_values, self.data["train_df"])
        print('\n')

    
