from typing import Dict, List
from h1st.model.oracle.oracle_modeler import OracleModeler
from .ts_oracle import TimeSeriesOracle
from h1st.model.oracle.student import AdaBoostModeler, AdaBoostModel, RandomForestModeler, RandomForestModel
from h1st.model.predictive_model import PredictiveModel

class TimeseriesOracleModeler(OracleModeler):
    def __init__(self, teacher: PredictiveModel,
                 ensembler_modeler: PredictiveModel,
                 student_modelers: List = [RandomForestModeler(RandomForestModel),
                                           AdaBoostModeler(AdaBoostModel)],
                 model_class = TimeSeriesOracle
                 ):
        self.teacher = teacher
        self.student_modelers = student_modelers
        self.ensembler_modeler = ensembler_modeler
        self.model_class = model_class
        self.stats = {}

    def build_model(self, data: Dict, id_col: str = None, ts_col: str = None, features: List = None) -> TimeSeriesOracle:
        '''
        Build the oracle
        :param data: a dictionary {'X': ...}
        :param id_col: id column that contains entity ids such as `equipment_id`
        :param ts_col: time-granularity column to group the data
        '''

        self.stats['id_col'] = id_col
        self.stats['ts_col'] = ts_col

        return super().build_model(data, features)