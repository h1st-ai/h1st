import shap


class SHAPModelDescriber:
    def __init__(self, describable_dict):
        self._model = describable_dict['base_model']
        self.data = describable_dict['data']
        self._get_shap_describer()
        self._get_shap_values()
        # self._plot_shap_describer()

    def _plot_shap_describer(self):
        shap.summary_plot(self.shap_values, self.data['train_df'])

    def _get_shap_describer(self):
        self.shap_describer = shap.TreeExplainer(self._model)

    def _get_shap_values(self):
        self.shap_values = self.shap_describer.shap_values(
            self.data["train_df"], check_additivity=False)
