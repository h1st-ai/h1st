import numpy as np
import lime.lime_tabular as lt

class LIMEModelExplainer:
    def __init__(self, decision, model, data):
        self.model = model
        self.data = data
        self.feature_names = list(self.data["train_df"].columns)
        self.decision_input = decision[0]
        self.lime_explainer()
        self.explain_decision()
        ## Only for testing if plots are generated
        # self.plot_lime_explanation()

    def plot_lime_explanation(self):
        self.explanation.show_in_notebook(show_table=True, show_all=False)

    def explain_decision(self):
        self.explanation = self.explainer.explain_instance(
            self.decision_input,
            self.model.predict,
        )

    def lime_explainer(self):
        self.explainer = lt.LimeTabularExplainer(
            np.array(self.data["train_df"]),
            feature_names=self.feature_names,
            verbose=False,
            mode="regression",
        )
