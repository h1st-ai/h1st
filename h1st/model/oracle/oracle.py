"""
Oracle architecture:

@startuml
allowmixing

Component Oracle #EEE {
	Class Teacher
	Class Student
	Class Ensemble
}

Actor "AI Engineer" as User

User .down.> TeacherModeler : uses
User .down.> StudentModeler : uses

TeacherModeler -down-> Teacher : builds
StudentModeler -down-> Student : builds
Teacher .right.> Student : teaches



Teacher -down-> Ensemble : trains
Student -down-> Ensemble : trains

Note as N1  #green
<size:16><color:white>Construction Phase</color></size>
end Note
@enduml

@startuml
allowmixing

Component Oracle #EEE {
    Class Teacher <<RuleBasedModel>>
    Class Student <<ML Generalizer>>
	Class Ensemble
}

Database Data
Circle Prediction

Data -down-> Teacher
Data -down-> Student

Teacher -down-> Ensemble : votes
Student -down-> Ensemble : votes

Ensemble -down-> Prediction

Note as N1  #green
<size:16><color:white>Execution Phase</color></size>
end Note
@enduml
"""

from typing import Dict, NoReturn, List
import pandas as pd
from h1st.model.predictive_model import PredictiveModel

from .student import RandomForestModeler, AdaBoostModeler
from .ensemble import Ensemble


class Oracle(PredictiveModel):
    """
    Oracle Model in Oracle framework
    """

    def __init__(self, teacher: PredictiveModel,
                 student_modelers: List = [RandomForestModeler(), AdaBoostModeler()],
                 ensemble: Ensemble = Ensemble):
        """
        :param teacher: The knowledge model.
        :param student_modelers: The student modelers.
        :param ensemble: The ensemble model class.
        """
        self.teacher = teacher
        self.student_modelers = student_modelers
        self.ensemble = ensemble()
        self.stats = {}

    def build(self, data: Dict, features: List = None) -> NoReturn:
        """
        Build the student and ensemble components.
        :param data: Unlabeled data.
        """
        self.stats['features'] = features
        # Generate features to get students' predictions
        train_data = self.generate_data(data)

        # Train the student model
        self.students = [student_modeler.build_model(train_data)
                         for student_modeler in self.student_modelers]

    def generate_data(self, data: Dict) -> Dict:
        """
        Generate data to train Student models.
        Return a copy of the provided data by default.
        Override this function to implement custom data generation
        :param data: unlabelled data.
        :returns: a dictionary of features and teacher's prediction.
        """
        if 'X' not in data:
            raise ValueError('Please provide data in form of {\'X\': pd.DataFrame}')

        df = data['X']

        features = self.stats['features']
        if features is not None:
            df = df[features]

        teacher_pred = self.teacher.predict({'X': df})
        if 'predictions' not in teacher_pred:
            raise KeyError('Teacher\'s output must contain a key named `predictions`')
        return {'X': df.copy(), 'y': pd.Series(teacher_pred['predictions'])}

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data. The Oracle expects the same features provided during `build` phase to be in the provided data. It automatically process the data the same way to that of the `build` phase.

        :params input_data: an dictionary with key `X` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        if not hasattr(self, 'students'):
            raise RuntimeError('No student built')

        # Generate features to get students' predictions
        predict_data = self.generate_data(input_data)

        # Generate student models' predictions
        student_preds = [student.predict(predict_data)['predictions'] for student in self.students]

        return self.ensemble.predict({'teacher_pred': predict_data['y'], 'student_preds': student_preds})

    def persist(self, version=None):
        if not hasattr(self, 'students'):
            raise RuntimeError('No student built')

        for student in self.students:
            version = student.persist(version)
        super().persist(version)

    def load_params(self, version: str = None) -> None:
        self.students = []
        for student_modeler in self.student_modelers:
            student = student_modeler.model_class()
            student.load_params(version)
            self.students.append(student)
        super().load_params(version)
