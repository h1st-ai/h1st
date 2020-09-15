import shap

class SHAPModelDescriber:
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.get_shap_describer()
        self.get_shap_values()
        ## Only for testing if plots are generated
        # self.plot_shap_describer()

    def plot_shap_describer(self):
        shap.summary_plot(self.shap_values, self.data['train_df'])

    def get_shap_describer(self):
        self.shap_describer = shap.TreeExplainer(self.model)

    def get_shap_values(self):
        self.shap_values = self.shap_describer.shap_values(
            self.data["train_df"], check_additivity=False
        )
