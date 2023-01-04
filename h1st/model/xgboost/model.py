from xgboost import XGBRegressor

from h1st.model.predictive_model import PredictiveModel


class XGBoost(PredictiveModel):
    def __init__(self) -> None:
        self.model = XGBRegressor

    def predict(self, input_data: dict) -> dict:
        result = self.model.predict(input_data)
        return {'predictions': result}
