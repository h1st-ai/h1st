from typing import List
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier

from h1st.model.model import Model
from h1st.core.exception import ModelException
from h1st.core.ensemble import ClassifierStackEnsemble

class RandomForestClassifierStackEnsemble(ClassifierStackEnsemble):
    """
    A ready to use StackEnsemble for classifier with ensembler is a sklearn's MultiOutputClassifier using RandomForestClassifier

    Each sub model must be a subclass of h1.Model and its .predict() method will receive an input data as a dictionary that has 'X' key and numeric value
    and return a dictionary with 'predictions' key and its prediction value

    .. code-block:: python
        :caption: Sub model for a StackEnsemble Example

        class Model1(h1.Model):
            def predict(self, data):
                X = data['X']
                ...
                return {'predictions': }

    .. code-block:: python
        :caption: RandomForestClassifierStackEnsemble usage Example

        class Model2(h1.Model):
                def predict(self, data):
                    X = data['X']
                    ...
                    return {'predictions': }

        class RandomForestClassifierStackEnsemble(ClassifierStackEnsemble):
            def __init__(self):
                super().__init__([
                    Model1().load('version_of_model_1'),
                    Model2().load('version_of_model_2')
                ])

            def load_data(self,):
                ...
                return loaded_data

            def prep(self, loaded_data):
                ...
                return prepared_data

        m1 = Model1()

        m1.load_prep_train_eval()
        ## Equivalent to
        # loaded_data = m1.load_data()
        # prepared_data = m1.prep(loaded_data)
        # m1.train(prepared_data)
        # m1.evaluate(prepared_data)

        print(m1.metrics)
        m1.persist('version_of_model_1')

        m2 = Model2()
        m2.load_prep_train_eval()
        print(m2.metrics)
        m2.persist('version_of_model_2')

        ensemble = RandomForestClassifierStackEnsemble(
            [Model1().load('version_of_model_1'),
             Model2().load('version_of_model_2')])
        ensemble.load_prep_train_eval()
        print(ensemble.metrics)
        ensemble.persist('version_of_model_ensemble')
        ensemble.predict(...)
    """

    def __init__(self, sub_models: List[Model], **kwargs):
        super().__init__(
            # MultiOutputClassifier(RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42)),
            RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42),
            sub_models,
            **kwargs
        )
