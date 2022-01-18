from typing import Dict, NoReturn
from h1st.model.predictive_model import PredictiveModel

from .student import Student, StudentModeler
from .ensemble import Ensemble

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
"""

"""
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

class Oracle(PredictiveModel):
    """
    Oracle Model in Oracle framework
    """
    def __init__(self, knowledge_model: PredictiveModel, student_modeler: StudentModeler = StudentModeler, student: Student = Student, ensemble: Ensemble = Ensemble):
        self.metas = {}
        self.teacher = knowledge_model
        self.ensemble = ensemble()
        self.student_modeler = student_modeler()
        self.student_modeler.model_class = student

    def build(self, data:Dict) -> NoReturn:
        # Generate knowledge_model's prediction
        teacher_pred = self.teacher.predict(data)['pred']

        # Train the student model
        self.student = self.student_modeler.build_model({'X': data['X'], 'y': teacher_pred})

    def predict(self, input_data: dict) -> dict:
        if not hasattr(self, 'student'):
            raise RuntimeError('No student built')

        # Generate knowledge_model's prediction
        teacher_pred = self.teacher.predict(input_data)
        # Generate student model's prediction
        student_pred = self.student.predict(input_data)

        return self.ensemble.predict({'teacher_pred': teacher_pred['pred'], 'student_pred': student_pred['pred']})

    def persist(self, version=None):
        if not hasattr(self, 'student'):
            raise RuntimeError('No student built')
        
        version = self.student.persist(version)
        super().persist(version)

    def load_params(self, version: str = None) -> None:
        self.student = self.student_modeler.model_class()
        self.student.load_params(version)
        super().load_params(version)
