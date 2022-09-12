from typing import Dict, Any

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.predictive_model import PredictiveModel


class MajorityVotingEnsemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Combine output of teacher and students using majority vote by default. In case
        when majority vote cannot be applied, use teacher's output as the final output.
        Inherit and override this method to use your custom combining approach.
        :param teacher_pred: teacher's prediction
        :param student_pred: student's prediction
        :returns: a dictionary with key `predictions` containing the predictions
        """
        predictions = input_data["x"].mode(axis="columns", numeric_only=True)[0]
        return {"predictions": predictions}


class GradBoostEnsemble(MLModel):
    def predict(self, input_data: Dict) -> Dict:
        y = self.base_model.predict(input_data["x"])
        return {"predictions": y}


class GradBoostEnsembleModeler(MLModeler):
    def __init__(self, model_class=GradBoostEnsemble):
        self.model_class = model_class
        self.stats = {}

    def evaluate_model(self, data: Dict, model: MLModel) -> Dict:
        super().evaluate_model(data, model)
        X, y_true = data["x_test"], data["y_test"]
        y_pred = pd.Series(model.predict({"x": X, "y": y_true})["predictions"])
        return {"r2_score": metrics.r2_score(y_true, y_pred)}

    def train_base_model(self, data: Dict[str, Any]) -> Any:
        X, y = data["x_train"], data["y_train"]
        model = GradientBoostingClassifier()
        model.fit(X, y)
        return model
