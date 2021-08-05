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

    def __init__(self, ensembler: MultiOutputClassifier, sub_models: List[Model], **kwargs):
        super().__init__(ensembler, sub_models, **kwargs)

    def evaluate(self, prepared_data: Dict, metrics: List[str]=None) -> NoReturn:
        """
        Evaluates for the test data
        :param prepared_data: a dictionary {'X_test': ..., 'y_test': ...}
        :param metrics: list of metrics to return and to persist later by the model.
            Default value = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']

        """
        def add_metric(name, value):
            if name in metrics:
                self.metrics[name] = value

        if not metrics:
            metrics = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']

        X_test, y_test = prepared_data['X_test'], prepared_data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']
        
        precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred)

        add_metric('confusion_matrix', confusion_matrix(y_test, y_pred))        
        add_metric('precision', precision)
        add_metric('recall', recall)
        add_metric('f1', f1)
        add_metric('support', support)
        add_metric('accuracy', accuracy_score(y_test, y_pred))
