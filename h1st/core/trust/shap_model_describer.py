import shap
from h1st.core.trust.describer import Describer


class SHAPModelDescriber(Describer):
    def __init__(self, base_model, data_to_describe):
        self.model_describer(base_model, data_to_describe)
        # self._plot_shap_describer(data_to_describe)

    def model_describer(self, base_model, data_to_describe):
        self._get_shap_describer(base_model)
        self._get_shap_values(data_to_describe)

    def _plot_shap_describer(self, data_to_describe):
        shap.summary_plot(self.shap_values, data_to_describe)

    def _get_shap_describer(self, base_model):
        self.shap_describer = shap.TreeExplainer(base_model)

    def _get_shap_values(self, data_to_describe):
        self.shap_values = self.shap_describer.shap_values(
            data_to_describe, check_additivity=False)
