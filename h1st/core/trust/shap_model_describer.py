import shap


class SHAPModelDescriber:
    def __init__(self, base_model, data):
        self._model = base_model[1]
        self.data = data[1]
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
