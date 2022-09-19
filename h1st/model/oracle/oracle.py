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

import logging
from typing import Dict, List
import pandas as pd
from h1st.model.predictive_model import PredictiveModel


class Oracle(PredictiveModel):
    """
    Oracle Model in Oracle framework
    """

    def __init__(self):
        """
        """
        self.stats = {}

    @classmethod
    def create_oracle(cls,
                      teacher: PredictiveModel,
                      students: List[PredictiveModel],
                      ensembler: PredictiveModel):
        """
        :param teacher: The knowledge model.
        :param student_modelers: The student modelers.
        :param ensemble: The ensemble model class.
        """
        model = cls()
        model.teacher = teacher
        model.students = students
        model.ensembler = ensembler
        return model

    @classmethod
    def generate_features(cls, data: Dict):
        return {'data': data['data'].copy()}

    @classmethod
    def generate_data(cls, data: Dict, teacher: PredictiveModel, stats: Dict) -> Dict:
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

        features = stats['features']
        if features is not None:
            df = df[features]

        df = cls.generate_features({'data': df})['data']

        teacher_pred = teacher.predict({'X': df})
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
        predict_data = self.__class__.generate_data(input_data, self.teacher,
                                                    self.stats)

        # Generate student models' predictions
        student_preds = [pd.Series(student.predict(predict_data)['predictions'])
                         for student in self.students]

        out = self.ensembler.predict(
            {'X': pd.concat(student_preds + [predict_data['y']], axis=1)}
        )
        return out

    def persist(self, version=None):
        """
        persist all pieces of oracle and store versions & classes
        """
        model_details = {}
        version = self.ensembler.persist(version)
        model_details['ensembler_class'] = self.ensembler.__class__
        model_details['ensembler_version'] = version

        student_classes = []
        student_versions = []
        for student in self.students:
            version = student.persist(version)
            student_classes.append(student.__class__)
            student_versions.append(version)

        model_details['student_classes'] = student_classes
        model_details['student_versions'] = student_versions
        model_details['teacher_class'] = self.teacher.__class__
        model_details['teacher_version'] = self.teacher.persist(version)
        self.stats['model_details'] =  model_details

        super().persist(version)
        return version

    def load(self, version: str = None) -> None:
        """
        load all pieces of oracle, return complete oracle
        """
        super().load(version)
        info = self.stats['model_details']
        ensembler = info['ensembler_class']().load(
            info['ensembler_version']
        )
        teacher = info['teacher_class']().load(
            info['teacher_version']
        )

        students = []
        for sclass, sversion in zip(info['student_classes'],
                                    info['student_versions']):
            students.append(sclass().load(sversion))

        self.ensembler = ensembler
        self.students = students
        self.teacher = teacher
        return self

    # Make it backward compatible.
    def load_params(self, version: str=None) -> None:
        return self.load(version)
