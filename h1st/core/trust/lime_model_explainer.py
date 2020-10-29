import numpy as np
import lime.lime_tabular as lt
from h1st.core.trust.explainer import Explainer


class LIMEModelExplainer(Explainer):
    def __init__(self, decision_input, model, train_data, mode="regression"):
        self._explainer_mode = mode
        self._feature_names = list(train_data.columns)
        self.decision_explainer(decision_input, model, train_data)

        # self._plot_lime_explanation()

    def decision_explainer(self, decision_input, model, train_data):
        self._get_lime_explainer(train_data)
        self._get_explanation(decision_input, model)

    # def _plot_lime_explanation(self):
    #     self._explanation.show_in_notebook(show_table=True, show_all=False)

    def _get_explanation(self, decision_input, model):
        self._explanation = self._explainer.explain_instance(
            decision_input,
            model.predict,
        )

    def _get_lime_explainer(self, train_data):
        self._explainer = lt.LimeTabularExplainer(
            np.array(train_data),
            feature_names=self._feature_names,
            verbose=False,
            mode=self._explainer_mode,
        )
