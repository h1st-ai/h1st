import shap


class SHAPModelDescriber:
    def __init__(self, model, data):
        self._model = model
        self._data = data
        self._get_shap_describer()
        self._get_shap_values()
        # self._plot_shap_describer()

    def _plot_shap_describer(self):
        shap.summary_plot(self._shap_values, self._data['train_df'])

    def _get_shap_describer(self):
        self._shap_describer = shap.TreeExplainer(self._model)

    def _get_shap_values(self):
        self._shap_values = self._shap_describer.shap_values(
            self._data["train_df"], check_additivity=False)
