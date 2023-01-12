from h1st.model.xgboost.model import XGBRegressionModel

class XGBClassifierModel(XGBRegressionModel):
    name = 'XGBClassifierModel'

    def predict(self, input_data: dict) -> dict:
        pred = super().predict(input_data)[self.output_key]
        pred = pred.applymap(self.apply_threshold)
        return {self.output_key: pred}

    def apply_threshold(self, x):
        return x > self.stats['threshold']

    def set_threshold(self, threshold: float):
        self.stats['threshold'] = threshold

