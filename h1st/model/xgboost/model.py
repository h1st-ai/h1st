import pandas as pd
import pytz

from datetime import datetime

from h1st.model.ml_model import MLModel


class XGBRegressionModel(MLModel):

    data_key = 'X'
    output_key = 'predictions'
    name = 'XGBRegressionModel'

    def __init__(self) -> None:
        super().__init__()

    def predict(self, input_data: dict) -> dict:
        X = input_data[self.data_key]
        output_col = self.stats['result_key']
        results = {}
        # Saving prediction time
        now = pytz.UTC.localize(datetime.utcnow())
        results['prediction_time'] = now.isoformat()
        # Scaling the input data
        scaler = self.stats['scaling_model']
        features = self.stats['scaled_features']
        selected_features = self.stats['selected_features']
        X_prime = pd.DataFrame(scaler.transform(X[features]), columns=features)
        X_prime = X_prime[selected_features]

        # Model Prediction
        pred = self.base_model.predict(X_prime)
        results[self.output_key] = pd.DataFrame(
            pred, columns=[output_col], index=X.index
        )
        return results
