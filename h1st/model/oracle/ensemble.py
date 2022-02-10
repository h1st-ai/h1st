from typing import Dict
import pandas as pd
from h1st.model.predictive_model import PredictiveModel


class Ensemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """

    def combine(self, teacher_pred, student_preds):
        '''
        Combine output of teacher and students using majority vote by default. In case
        when majority vote cannot be applied, use teacher's output as the final output.
        Inherit and override this method to use your custom combining approach.
        :param teacher_pred: teacher's prediction
        :param student_pred: student's prediction
        :returns: a dictionary with key `predictions` containing the predictions
        '''
        if len(student_preds) == 1:
            predictions = student_preds[0]
        else:
            pred_dict = {'teacher_pred': teacher_pred}
            pred_dict.update({f'student_pred_{i}': student_pred
                              for i, student_pred in enumerate(student_preds)})
            predictions = pd.DataFrame(pred_dict).mode(axis='columns', numeric_only=True)[0]

        return {'predictions': predictions}

    def predict(self, input_data: Dict) -> Dict:
        teacher_pred = pd.Series(input_data['teacher_pred'])
        student_preds = [pd.Series(student_pred) for student_pred in input_data['student_preds']]
        return self.combine(teacher_pred, student_preds)
