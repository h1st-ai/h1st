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
from collections import defaultdict

import pandas as pd
import sklearn

from h1st.model.fuzzy.fuzzy_model import FuzzyModel
from h1st.model.ensemble.stack_ensemble import StackEnsemble
from h1st.model.predictive_model import PredictiveModel
from h1st.model.ml_model import MLModel
from h1st.model.rule_based_model import RuleBasedModel

class Oracle(PredictiveModel):
    """
    Oracle Model in Oracle framework
    """

    def __init__(self):
        self.stats = {}

    @classmethod
    def construct_oracle(cls,
                      teacher: RuleBasedModel,
                      students: list[MLModel],
                      ensemblers: PredictiveModel):
        """
        :param teacher: The knowledge model.
        :param students: The student model.
        :param ensemble: The ensemble model class.
        """
        model = cls()
        model.teacher = teacher
        model.students = students
        model.ensemblers = ensemblers
        return model

    # @classmethod
    # def generate_features(cls, data: Dict):
    #     return {'data': data['data'].copy()}

    @classmethod
    def generate_teacher_prediction(cls, data: Dict, teacher: PredictiveModel, stats: Dict) -> Dict:
        """
        Generate data to train Student models.
        Return a copy of the provided data by default.
        Override this function to implement custom data generation
        :param data: unlabelled data.
        :returns: a dictionary of features and teacher's prediction.
        """
        if 'x' not in data:
            raise ValueError('Please provide data in form of {\'X\': pd.DataFrame}')

        df = data['x']

        features = stats['features']
        if features is not None:
            df = df[features]

        # df = cls.generate_features({'data': df})['data']
        teacher_pred = teacher.predict({'x': df})
        if 'predictions' not in teacher_pred:
            raise KeyError('Teacher\'s output must contain a key named `predictions`')

        
        return teacher_pred['predictions']
        # return {'x': df.copy(), 'y': teacher_pred['predictions']}

    def predict(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data. The Oracle expects the same features provided during `build` phase to be in the provided data. It automatically process the data the same way to that of the `build` phase.

        :params input_data: an dictionary with key `x` containing the data to get predictions.
        :returns: a dictionary with key `predictions` containing the predictions
        """
        if not hasattr(self, 'students'):
            raise RuntimeError('No student built')
        if not hasattr(self, 'ensemblers'):
            raise RuntimeError('No ensemblers built')            

        # Generate features to get students' predictions
        teacher_prediction = self.__class__.generate_teacher_prediction(
            input_data, self.teacher, self.stats)
        predictions = {}
        for col in teacher_prediction:
            # Generate student models' predictions
            student_preds = [pd.Series(student.predict(input_data)['predictions'],
                                       name=f'stud_{idx}_{col}')
                            for idx, student in enumerate(self.students[col])]
            predictions[col] = self.ensemblers[col].predict(
                {'x': pd.concat(student_preds + [teacher_prediction[col]], axis=1)}
            )['predictions']
        return {'predictions': predictions}

    def persist(self, version=None):
        """
        persist all pieces of oracle and store versions & classes
        """
        model_details = {}
        student_details = {}
        ensembler_details = {}
        for label in self.stats['labels']:
            student_classes = []
            student_versions = []
            for idx, student in enumerate(self.students[label]):
                student_classes.append(student.__class__)
                student_versions.append(
                    student.persist(f'student_{version}_{label}_{idx}'))
            student_details[label] = {
                'class': student_classes,
                'version': student_versions
            }
            ensembler_details[label] = {
                'class': self.ensemblers[label].__class__,
                'version': self.ensemblers[label].persist(f'ensembler_{version}_{label}')
            }
        model_details['teacher_details'] = {
            'class': self.teacher.__class__,
            'version': self.teacher.persist(f'teacher_{version}')
        }
        model_details['student_details'] = student_details
        model_details['ensembler_details'] = ensembler_details
        self.stats['model_details'] =  model_details
        super().persist(version)
        return version

    def load(self, version: str = None) -> None:
        """
        load all pieces of oracle, return complete oracle
        """
        super().load(version)
        info = self.stats['model_details']
        teacher = info['teacher_details']['class']().load(
            info['teacher_details']['version']
        )
        ensemblers = {}
        students = defaultdict(list)
        for label in self.stats['labels']:
            ensemblers[label] = info['ensembler_details'][label]['class']().load(
                info['ensembler_details'][label]['version']
            )
            for s_class, s_version in zip(info['student_details'][label]['class'],
                                          info['student_details'][label]['version']):
                students[label].append(s_class().load(s_version))

        self.teacher = teacher
        self.students = students
        self.ensemblers = ensemblers
        return self

    # Make it backward compatible.
    def load_params(self, version: str=None) -> None:
        return self.load(version)
