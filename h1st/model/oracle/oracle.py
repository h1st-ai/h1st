from h1st.model.ml_model import MLModel
from h1st.model.ml_model import MLModel

from student import Student, StudenModeler
from teacher import Teacher, TeacherModeler
from ensemble import Ensemble

"""
Oracle architecture:

@startuml
allowmixing

Class Teacher <<RuleBasedModel>>
Class Student <<ML Generalizer>>
Actor User

User .right.> Teacher  : creates
Teacher -right-> Student : teaches

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
Circle Data
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

class Oracle(MLModel):
    """
    Teacher Model in Oracle framework
    """
    pass