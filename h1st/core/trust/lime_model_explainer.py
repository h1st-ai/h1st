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
        self.positive, self.negative = self._get_feature_contribution(
            decision_input, train_data)

    def _generate_lime_explanation_report(self):
        pass

    def _plot_lime_explanation(self):
        self._explanation.show_in_notebook(show_table=True, show_all=True)

    def _get_explanation(self, decision_input, model):
        self._explanation = self._explainer.explain_instance(
            decision_input, model.predict)

    def _get_lime_explainer(self, train_data):
        self._explainer = lt.LimeTabularExplainer(
            np.array(train_data),
            feature_names=self._feature_names,
            verbose=False,
            mode=self._explainer_mode,
        )

    def _get_feature_stats(self, train_data, feature):
        _dict = {}

        def get_threshold(tmp_df):
            return tmp_df.nunique() / tmp_df.shape[0]

        def get_quantiles(tmp_df):
            quantiles = [0.25, 0.50, 0.75, 1]
            return [tmp_df.quantile(quantile) for quantile in quantiles]

        if get_threshold(train_data[feature]) > 0.0075:
            quantiles = get_quantiles(train_data[feature])
            return ['numerical', quantiles]
        else:
            return ['categorical']

    def _get_feature_contribution(self, decision_input, train_data):
        import re
        positive_features = {}
        negative_features = {}
        for feature_items in self._explanation.as_list():
            _list_feature_items = re.split(r'\s', feature_items[0])
            for item in _list_feature_items:
                if re.search('[a-zA-Z]', item):
                    stats = self._get_feature_stats(train_data, item)
                    if feature_items[1] < 0:
                        negative_features[item] = [
                            abs(float('%0.2f' % (feature_items[1] * 100))),
                            decision_input[item], stats
                        ]
                    if feature_items[1] > 0:
                        positive_features[item] = [
                            abs(float('%0.2f' % (feature_items[1] * 100))),
                            decision_input[item], stats
                        ]
        return positive_features, negative_features
