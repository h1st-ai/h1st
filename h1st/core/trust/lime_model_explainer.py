import numpy as np
import lime.lime_tabular as lt


class LIMEModelExplainer:
    def __init__(self, decision, describable_dict):
        self._model = describable_dict['base_model']
        self._data = describable_dict['data']
        self.feature_names = list(self._data["train_df"].columns)
        self.decision_input = decision[0]
        self._lime_explainer()
        self._explain_decision()
        # self._plot_lime_explanation()

    def _plot_lime_explanation(self):
        self.explanation.show_in_notebook(show_table=True, show_all=False)

    def _explain_decision(self):
        self.explanation = self.explainer.explain_instance(
            self.decision_input,
            self._model.predict,
        )

    def _lime_explainer(self):
        self.explainer = lt.LimeTabularExplainer(
            np.array(self._data["train_df"]),
            feature_names=self.feature_names,
            verbose=False,
            mode="regression",
        )
