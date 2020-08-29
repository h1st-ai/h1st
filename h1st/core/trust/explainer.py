import numpy as np
import pandas as pd
import shap
import lime
import lime.lime_tabular as lt
import mpld3 as mpl


# class Explainer:
#     def __init__(self, h1stmodel, data):
#         self.model = h1stmodel.model
#         self.data = data
#         self.model_type = type(h1stmodel.model).__name__

#         def get_explainer(self):
#             """
#             Implement logic of training model

#             """
#             # not raise NotImplementedError so the initial model created by integrator will just work
#             pass


class SHAPExplainer:
    def __init__(self, h1stmodel, data):
        self.model = h1stmodel.model
        self.data = data
        self.model_type = type(h1stmodel.model).__name__
        self.get_shap_explainer()
        self.get_shap_values()
        self.generate_plots()

    # def get_explainer_type(self):
    #     if self.model_type == 'RandomForestRegressor':
    #         return

    def _shap_local_plot(self, j):
        explainer_model = shap.TreeExplainer(self.model)
        shap_values_model = explainer_model.shap_values(self.samples)
        print(
            explainer_model.expected_value, shap_values_model[j], self.samples.iloc[[j]]
        )
        # print(explainer_model.expected_value[0])
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

    def generate_plots(self):
        shap.initjs()
        df = self.data["train_df"].reset_index(drop=True)
        shap.summary_plot(self.shap_values, self.data["train_df"])
        shap.dependence_plot("alcohol", self.shap_values, self.data["train_df"])
        # shap.plots.force.visualize(
        #     self.shap_explainer.expected_value, self.shap_values[0], df.iloc[[0]]
        # )
        # print(self.shap_explainer.expected_value, self.shap_values[0])
        # print(df.iloc[0:1, :])

        shap.force_plot(self.shap_explainer.expected_value, self.shap_values, df)

        # self.samples = self._random_sample_generator()
        # # print(self.samples)

        # explainer_model = shap.TreeExplainer(self.model)
        # shap_values_model = explainer_model.shap_values(self.samples)

        # # print(explainer_model.expected_value[0])
        # shap.force_plot(
        #     explainer_model.expected_value,
        #     shap_values_model[1],
        #     self.samples.iloc[[1]],
        # )

        # for idx in range(0, 1, 1):
        #     self._shap_local_plot(idx)


class LIMEExplainer:
    def __init__(self, h1stmodel, data):
        self.model = h1stmodel.model
        self.data = data
        self.model_type = type(h1stmodel.model).__name__
        self.features = list(self.data["train_df"].columns)
        self.get_lime_explainer()
        self.plot_lime_explain()

    def _get_sample_lime_explain(self):
        idx = np.random.randint(0, self.data["train_df"].shape[0], 1)[0]
        # print(idx, self.data["train_df"].shape[0])
        # print(self.data["train_df"].iloc[[idx]])
        return self.lime_explainer.explain_instance(
            self.data["train_df"].reset_index(drop=True).iloc[idx], self.model.predict
        )

    def get_lime_explainer(self):
        if self.model_type == "RandomForestRegressor":
            self.lime_explainer = lt.LimeTabularExplainer(
                np.array(self.data["train_df"]),
                feature_names=self.features,
                # class_names=['Label'],
                # categorical_features=,
                # There is no categorical features in this example, otherwise specify them.
                verbose=True,
                mode="regression",
            )

    def plot_lime_explain(self):
        self._get_sample_lime_explain().show_in_notebook(
            show_table=True, show_all=False
        )
