from typing import Any, Dict
from copy import deepcopy
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler


class Student(MLModel):
    """
    Knowledge Generalization Model
    """

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data

        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        return {'predictions': self.base_model.predict(input_data['X'])}


class StudentModeler(MLModeler):
    """
    Knowledge Generalization Modeler
    """

    def __init__(self, base_model=LogisticRegression()):
        self.model_class = Student
        self.base_model = base_model

    def train_base_model(self, prepared_data: Dict[str, Any]) -> Any:
        self.base_model.fit(prepared_data['X'], prepared_data['y'])
        return deepcopy(self.base_model)


class RandomForestModel(Student):
    """
    Knowledge Generalization Model backed by a RandomForest algorithm
    """
    pass


class RandomForestModeler(StudentModeler):
    """
    Knowledge Generalization Modeler backed by a RandomForest algorithm.
    """

    def __init__(self, base_model=RandomForestClassifier()):
        super().__init__(base_model=base_model)
        self.model_class = RandomForestModel


class AdaBoostModel(Student):
    """
    Knowledge Generalization Model backed by an AdaBoost algorithm
    """
    pass


class AdaBoostModeler(StudentModeler):
    """
    Knowledge Generalization Modeler backed by a AdaBoost algorithm.
    """

    def __init__(self, base_model=AdaBoostClassifier()):
        super().__init__(base_model=base_model)
        self.model_class = AdaBoostModel
