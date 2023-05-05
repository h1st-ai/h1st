from h1st.model.ml.xgboost.regression import XGBRegressionModel, XGBRegressionModeler


class XGBClassifierModel(XGBRegressionModel):
    name = 'XGBClassifier'

    def predict(self, input_data: dict) -> dict:
        pred = super().predict(input_data)[self.output_key]
        pred = pred.applymap(self.apply_threshold)
        return {self.output_key: pred}

    def apply_threshold(self, x):
        return 1 if x >= self.stats['threshold'] else 0

    def set_threshold(self, threshold: float):
        self.stats['threshold'] = threshold


class XGBClassifierModeler(XGBRegressionModeler):
    model_class = XGBClassifierModel

    def __init__(self, threshold=0.5, **kwargs):
        super().__init__(**kwargs)
        self.stats['threshold'] = float(threshold)
