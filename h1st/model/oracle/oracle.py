from typing import Dict, List
from h1st.model.model import Model
from h1st.model.oracle.oracle_model import OracleModel


class Oracle(OracleModel):
    '''
    Keep the Oracle class for backward compability, will deprecate soon
    Use OracleModel instead to follow h1st convention
    '''

    def __init__(
        self,
        teacher: Model = None,
        students: Dict[str, List[Model]] = None,
        ensemblers: Dict[str, Model] = None,
    ):
        super().__init__(teacher, students, ensemblers)
