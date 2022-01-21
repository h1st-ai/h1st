from typing import Dict, NoReturn
import pandas as pd
from h1st.model.predictive_model import PredictiveModel
from .oracle import Oracle
from .student import Student, StudentModeler
from .ensemble import Ensemble

class TimeSeriesOracle(Oracle):
    def __init__(self, knowledge_model: PredictiveModel, student_modeler: StudentModeler = StudentModeler, student: Student = Student, ensemble: Ensemble = Ensemble):
        super().__init__(knowledge_model, student_modeler, student, ensemble)
        self.meta = {}

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
        group_names = []
        i = 0
        for group_name, group_df in df.groupby([id_col, ts_col]):
            if i >= 100:
                break
            group_names.append(group_name)
            # temporarily remove datetime column for now
            group_df.drop([id_col, ts_col, 'datetime'], axis=1, inplace=True)
            
            features.append(self.generate_features({'data': group_df}))

            i += 1

        return {'group_names': group_names, 'features': pd.concat(features)}


    def build(self, data: Dict, id_col: str, ts_col: str) -> NoReturn:
        '''
        Build the oracle
        :param data: a dictionary {'X': ...}
        :param id_col: id column that contains entity ids such as `equipment_id`
        :param ts_col: time-granuality column to group the data
        '''
        
        self.meta['id_col'] = id_col
        self.meta['ts_col'] = ts_col

        # Generate knowledge_model's prediction
        teacher_pred = self.teacher.predict(data)['pred']
        
        # Generate training data to train the student model
        training_data = self.generate_data(data, id_col, ts_col)

        # Train the student model
        self.student = self.student_modeler.build_model({'X': training_data['features'], 'y': teacher_pred})

    def predict(self, input_data: dict) -> dict:
        if not hasattr(self, 'student'):
            raise RuntimeError('No student built')

        # Generate knowledge_model's prediction
        teacher_pred = self.teacher.predict(input_data)

        # Generate features the student model
        predict_data = self.generate_data(input_data, self.meta['id_col'], self.meta['ts_col'])
        # Generate student model's prediction
        student_pred = self.student.predict({'X': predict_data['features']})

        return self.ensemble.predict({'teacher_pred': teacher_pred['pred'], 'student_pred': student_pred['pred']})
