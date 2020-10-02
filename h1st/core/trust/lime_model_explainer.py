import numpy as np
import lime.lime_tabular as lt


class LIMEModelExplainer:
    def __init__(self, decision, model, data):
        self._model = model
        self._data = data
        self._feature_names = list(self._data["train_df"].columns)
        self._decision_input = decision[0]
        self._lime_explainer()
        self._explain_decision()
        # self._plot_lime_explanation()

    def _plot_lime_explanation(self):
        self._explanation.show_in_notebook(show_table=True, show_all=False)

    def _explain_decision(self):
        self._explanation = self._explainer.explain_instance(
            self._decision_input,
            self._model.predict,
        )

    def _lime_explainer(self):
        self._explainer = lt.LimeTabularExplainer(
            np.array(self._data["train_df"]),
            feature_names=self._feature_names,
            verbose=False,
            mode="regression",
        )
