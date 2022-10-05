from typing import List

from h1st.model.ensemble.stack_ensemble_modeler import StackEnsembleModeler
from h1st.model.ml_modeler import MLModeler
from h1st.model.modeler import Modeler
from h1st.model.model import Model
from h1st.model.oracle.oracle_model import OracleModel
from h1st.model.oracle.student_modelers import LogisticRegressionModeler, RandomForestModeler
from h1st.model.oracle.ensemble_models import MajorityVotingEnsembleModel
from h1st.model.predictive_model import PredictiveModel
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler


# TODO: fuzzy model output is now like [0.2, 0.5, 0.4, 0.7]
# TODO: we can build multiple binary classifier or one multi-class classifier
# TODO: if student is multiple binary classifier, then ensemble also should be like that ?


class OracleModeler(Modeler):
    '''
    Modeler to build an Oracle model with a Model as the teacher,
    a list of Modeler as students and a list of Modeler as ensemblers.
    User can provide additional information like labeled data or fuzzy threshold to build model
    '''

    def __init__(self, model_class=None):
        self.stats = {}
        if model_class is None:
            self.model_class = OracleModel
        else:
            self.model_class = model_class

    def build_model(
        self,
        data: dict = None,
        teacher: Model = RuleBasedModel,
        students: List[Modeler] = [RandomForestModeler, LogisticRegressionModeler],
        ensembler: Modeler = RuleBasedModeler(MajorityVotingEnsembleModel),
        **kwargs
    ) -> Model:
        '''
        Build the components of Oracle, which are students and ensemblers.
        student is always MLModel and ensembler can be MLModel or RuleBasedModel.
        '''
        return self.model_class
