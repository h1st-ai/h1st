import pandas as pd
from h1st.model.predictive_model import PredictiveModel


class Ensemble(PredictiveModel):
    """
    Ensemble Model in Oracle framework
    """
    def predict(self, input_data: dict) -> dict:
        teacher_pred = pd.Series(input_data['teacher_pred'])
        student_pred = pd.Series(input_data['student_pred'])

        if set(teacher_pred.unique().tolist()) != set([0,1]) and\
            set(student_pred.unique().tolist()) != set([0,1]):
            raise ValueError('Only binary outputs are supported!!!')

        # AND-style combination for now
        return {'pred': teacher_pred & student_pred}
