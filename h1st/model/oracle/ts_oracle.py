from typing import Dict, NoReturn
import pandas as pd
from h1st.model.predictive_model import PredictiveModel
from .oracle import Oracle
from .student import Student, StudentModeler
from .ensemble import Ensemble

class TimeSeriesOracle(Oracle):
    def __init__(self, knowledge_model: PredictiveModel, student_modeler: StudentModeler = StudentModeler,
                student: Student = Student, ensemble: Ensemble = Ensemble):
        super().__init__(knowledge_model, student_modeler, student, ensemble)
        self.stats = {}

    def generate_features(self, data: Dict):
        df = data['data']
        ret = pd.DataFrame(df.values.reshape(1, df.shape[0]*df.shape[1]))
        return ret

    def generate_data(self, data: Dict, id_col: str, ts_col: str) -> Dict:
        df = data['X']

        if id_col not in df.columns:
            raise ValueError(f'{id_col} does not exist')

        if ts_col not in df.columns:
            raise ValueError(f'{ts_col} does not exist')

        features = []
        teacher_pred = []
        for group_name, group_df in df.groupby([id_col, ts_col]):
            # temporarily remove datetime column for now
            group_df.drop([id_col, ts_col], axis=1, inplace=True)
            teacher_pred.append(self.teacher.predict({'X': group_df})['pred'])
            
            features.append(self.generate_features({'data': group_df}))

        df_features = pd.concat(features).fillna(0)
        return {'X': df_features, 'y': pd.Series(teacher_pred)}


    def build(self, data: Dict, id_col: str, ts_col: str) -> NoReturn:
        '''
        Build the oracle
        :param data: a dictionary {'X': ...}
        :param id_col: id column that contains entity ids such as `equipment_id`
        :param ts_col: time-granuality column to group the data
        '''
        
        self.stats['id_col'] = id_col
        self.stats['ts_col'] = ts_col
        
        # Generate training data to train the student model
        training_data = self.generate_data(data, id_col, ts_col)
        # Train the student model
        self.student = self.student_modeler.build_model(training_data)

    def predict(self, input_data: dict) -> dict:
        if not hasattr(self, 'student'):
            raise RuntimeError('No student built')

        # Generate features the student model
        predict_data = self.generate_data(input_data, self.stats['id_col'], self.stats['ts_col'])
        # Generate student model's prediction
        student_pred = self.student.predict({'X': predict_data['X']})

        return self.ensemble.predict({'teacher_pred': predict_data['y'], 'student_pred': student_pred['pred']})
