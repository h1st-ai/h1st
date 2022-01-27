import pandas as pd
from h1st.model.predictive_model import PredictiveModel


class Ensemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """
    def combine(self, teacher_pred, student_pred):
        '''
        Provide default combination for multi-class outputs which prioritizes
        teacher's output in case of conflicts.
        Inherit and override this method to support other
        types of combination.
        :param teacher_pred: teacher's prediction
        :param student_pred: student's prediction
        '''
        pred = pd.DataFrame({'teacher_pred': teacher_pred, 'student_pred': student_pred})\
                 .apply(lambda row: row['teacher_pred'] 
                                    if row['teacher_pred'] == row['student_pred']
                                    else row['teacher_pred'], axis=1)

        return {'pred': pred}

    def predict(self, input_data: dict) -> dict:
        teacher_pred = pd.Series(input_data['teacher_pred'])
        student_pred = pd.Series(input_data['student_pred'])

        return self.combine(teacher_pred, student_pred)