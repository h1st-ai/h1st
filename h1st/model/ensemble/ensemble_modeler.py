from h1st.model.modeler import Modeler
from h1st.model.rule_based_modeler import RuleBasedModeler
from h1st.model.ensemble.ensemble import (
    LogicalOREnsemble, MajorityVotingEnsembleModel
)


class EnsembleModeler(Modeler):
    pass


class LogicalOREnsembleModeler(RuleBasedModeler):
    def __init__(self):
        super().__init__(LogicalOREnsemble)


class MajorityVotingEnsembleModeler(RuleBasedModeler):
    def __init__(self):
        super().__init__(MajorityVotingEnsembleModel)

