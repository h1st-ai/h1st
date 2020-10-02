from typing import Dict, List
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.multioutput import MultiOutputClassifier

from h1st.core.model import Model
from h1st.core.ensemble import StackEnsemble


class StackEnsembleClassifier(StackEnsemble):
    """StackEnsemble classifier

    This is the base class for stack ensemble classifiers
    """

    def __init__(self,
                 ensembler: MultiOutputClassifier,
                 sub_models: List[Model],
                 submodel_input_key,
                 submodel_output_key):
        super().__init__(
            ensembler,
            sub_models,
            submodel_input_key,
            submodel_output_key)

    def evaluate(self, data: Dict, metrics: List[str]=None) -> Dict:
        """
        Evaluates for the test data
        :param data: a dictionary {'X_test': ..., 'y_test': ...}
        :param metrics: list of metrics to return and to persist later by the model.
            Default value = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']
        
        :return:
            a dictionary containing requested metrics

        """
        def add_metric(name, value):
            if name in metrics:
                self.metrics[name] = value

        if not metrics:
            metrics = ['confusion_matrix', 'precision', 'recall', 'f1', 'support', 'accuracy']

        X_test, y_test = data['X_test'], data['y_test']
        y_pred = self.predict({'X': X_test})['predictions']     
        
        precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred)

        add_metric('confusion_matrix', confusion_matrix(y_test, y_pred))        
        add_metric('precision', precision)
        add_metric('recall', recall)
        add_metric('f1', f1)
        add_metric('support', support)
        add_metric('accuracy', accuracy_score(y_test, y_pred))

        return self.metrics
