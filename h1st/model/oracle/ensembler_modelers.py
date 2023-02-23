from typing import Any, Dict
from pandas import Series
from sklearn import metrics
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.oracle.ensembler_models import MLPEnsembleModel


class MLPEnsembleModeler(MLModeler):
    def __init__(self, model_class=None):
        self.stats = {}
        self.model_class = model_class if model_class is not None else MLPEnsembleModel

    def _preprocess(self, data):
        self.stats['scaler'] = StandardScaler()
        return self.stats['scaler'].fit_transform(data)

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        x = self._preprocess(prepared_data['X_train'])
        y = prepared_data['y_train']
        model = MLPClassifier(
            hidden_layer_sizes=(100, 100), random_state=1, max_iter=2000
        )
        model.fit(x, y)
        return model

    def evaluate_model(self, prepared_data: dict, model: MLModel) -> dict:
        super().evaluate_model(prepared_data, model)
        x, y_true = prepared_data['X_test'], prepared_data['y_test']
        y_pred = Series(model.predict({'X': x, 'y': y_true})['predictions'])
        return {'r2_score': metrics.r2_score(y_true, y_pred)}
