from typing import List
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier

from h1st.core.model import Model
from h1st.core.exception import ModelException
from h1st.core.ensemble import StackEnsembleClassifier

class RandomForestStackEnsembleClassifier(StackEnsembleClassifier):
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
        :caption: RandomForestStackEnsembleClassifier usage Example

        class Model2(h1.Model):
                def predict(self, data):
                    X = data['X']
                    ...
                    return {'predictions': }

        class RandomForestStackEnsembleClassifier(StackEnsembleClassifier):
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
        loaded_data = m1.load_data()
        prepared_data = m1.prep(loaded_data)
        m1.train(prepared_data)
        m1.evaluate(prepared_data)
        m1.persist('version_of_model_1')

        m2 = Model2()
        loaded_data = m2.load_data()
        prepared_data = m2.prep(loaded_data)
        m2.train(prepared_data)
        m2.evaluate(prepared_data)
        m2.persist('version_of_model_2')

        ensemble = RandomForestStackEnsembleClassifier(
            [Model1().load('version_of_model_1'),
             Model2().load('version_of_model_2')])
        loaded_data = ensemble.load_data()
        prepared_data = ensemble.prep(loaded_data)
        ensemble.train(prepared_data)
        ensemble.evaluate(prepared_data)
        ensemble.persist('version_of_model_ensemble')
        ensemble.predict(...)
    """

    def __init__(self,
                 sub_models: List[Model],
                 submodel_input_key='X',
                 submodel_output_key='predictions'):
        super().__init__(
            MultiOutputClassifier(RandomForestClassifier(n_jobs=-1, max_depth=4, random_state=42)),
            sub_models,
            submodel_input_key,
            submodel_output_key
        )
