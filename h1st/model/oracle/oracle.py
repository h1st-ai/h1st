from h1st.model.predictive_model import PredictiveModel

from student import Student, StudenModeler
from teacher import Teacher, TeacherModeler
from ensemble import Ensemble

"""
Oracle architecture:

@startuml
allowmixing

Class Teacher
Actor "AI Engineer" as User

User .down.> TeacherModeler : uses
User .down.> StudentModeler : uses

TeacherModeler -down-> Teacher : builds
StudentModeler -down-> Student : builds
Teacher .right.> Student : teaches



Teacher -down-> Oracle : trains
Student -down-> Oracle : trains

Note as N1  #green
<size:16><color:white>Construction Phase</color></size>
end Note
@enduml
"""

"""
@startuml
allowmixing

Class Teacher <<RuleBasedModel>>
Class Student <<ML Generalizer>>
Database Data
Circle Prediction

Data -down-> Teacher
Data -down-> Student

Teacher -down-> Oracle : votes
Student -down-> Oracle : votes

Oracle -down-> Prediction

Note as N1  #green
<size:16><color:white>Execution Phase</color></size>
end Note
@enduml
"""

class Oracle(PredictiveModel):
    """
    Teacher Model in Oracle framework
    """
    pass