from h1st.model.predictive_model import PredictiveModel


class OracleModel(PredictiveModel):
    def __init__(self, teacher = None, students = None, ensemblers = None):
        self.teacher = teacher
        self.students = students
        self.ensemblers = ensemblers
        self.stats = {}
