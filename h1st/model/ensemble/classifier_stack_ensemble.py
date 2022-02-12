from typing import Dict, List, NoReturn
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.multioutput import MultiOutputClassifier

from h1st.model.ensemble.stack_ensemble import StackEnsemble
from h1st.model.model import Model


class ClassifierStackEnsemble(StackEnsemble):
    """StackEnsemble classifier

    This is the base class for stack ensemble classifiers
    """

    def __init__(self, ensembler, sub_models: List[Model], **kwargs):
        super().__init__(ensembler, sub_models, **kwargs)