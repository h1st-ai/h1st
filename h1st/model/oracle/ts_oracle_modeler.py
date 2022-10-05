from h1st.model.model import Model
from h1st.model.modeler import Modeler
from h1st.model.oracle.oracle_modeler import OracleModeler
from h1st.model.oracle.ts_oracle_model import TimeSeriesOracleModel
from h1st.model.oracle.student_modelers import (
    RandomForestModeler,
    LogisticRegressionModeler,
)
from h1st.model.predictive_model import PredictiveModel


class TimeseriesOracleModeler(OracleModeler):
    def __init__(self, model_class=None):
        self.stats = {}
        self.model_class = (
            model_class if model_class is not None else TimeSeriesOracleModel
        )

    def build_model(
        self,
        data: dict = None,
        teacher: Model = PredictiveModel,
        students: list(Modeler) = [RandomForestModeler, LogisticRegressionModeler],
        ensembler: Modeler = Modeler,
        **kwargs
    ) -> Model:
        '''
        Build the oracle
        :param data: a dictionary {'X': ...}
        :param teacher: a Model to be used as the teacher in Oracle
        :param students: a list of Modelers to be used as students in Oracle
        :param ensembler: a Modeler to be used as an ensemble in Oracle
        :param id_col: id column that contains entity ids such as `equipment_id`
        :param ts_col: time-granularity column to group the data
        '''
        self.teacher = teacher
        self.students = students
        self.ensembler = ensembler
        self.stats['id_col'] = kwargs['id_col']
        self.stats['ts_col'] = kwargs['ts_col']
        return super().build_model(data, teacher, students, ensembler, **kwargs)
