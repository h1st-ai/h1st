from typing import Dict, Any

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics
from sklearn.preprocessing import StandardScaler

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.predictive_model import PredictiveModel


class MajorityVotingEnsemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Combine output of teacher and students using majority voting by default. In case
        when majority vote cannot be applied, use teacher's output as the final output.
        Inherit and override this method to use your custom combining approach.
        :param input_data: dictionary with `x` key and input data
        :returns: a dictionary with key `predictions` containing the predictions
        """
        predictions = input_data["x"].mode(axis="columns", numeric_only=True)[0]
        return {"predictions": predictions}


class GradBoostEnsemble(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        if isinstance(input_data["x"], pd.DataFrame):
            input_data["x"] = input_data["x"].values
        x = self.stats["scaler"].transform(input_data["x"])
        y = self.base_model.predict(x)
        return {"predictions": y}


class GradBoostEnsembleModeler(MLModeler):
    def __init__(self, model_class=GradBoostEnsemble):
        self.model_class = model_class
        self.stats = {}

    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        x, y_true = data["x_test"], data["y_test"]
        y_pred = pd.Series(model.predict({"x": x, "y": y_true})["predictions"])
        return {"r2_score": metrics.r2_score(y_true, y_pred)}

    def preprocess(self, data):
        self.stats["scaler"] = StandardScaler()
        return self.stats["scaler"].fit_transform(data)

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        from sklearn.neural_network import MLPClassifier

        x, y = data["x_train"], data["y_train"]
        x = self.preprocess(x)
        model = MLPClassifier(
            hidden_layer_sizes=(100, 100), random_state=1, max_iter=2000
        )
        # model = GradientBoostingClassifier()
        model.fit(x, y)
        return model
