from typing import Any, Dict
from sklearn.linear_model import LogisticRegression
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler


class Student(MLModel):
    """
    Knowledge Generalization Model
    """
    def predict(self, input_data: dict) -> dict:
        return {'pred': self.base_model.predict(input_data['X'])}


class StudentModeler(MLModeler):
    """
    Knowledge Generalization Modeler
    """
    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        model = LogisticRegression()
        model.fit(prepared_data['X'], prepared_data['y'])

        return model
