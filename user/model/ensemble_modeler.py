# from h1st.model.oracle_modeler import OracleModeler
import __init__
from h1st.model.ml_modeler import MLModeler

class EnsembleModeler():

    pass


class Ensemble:
    pass


class MyEnsemble(Ensemble):
    def predict(self):


class MyEnsembleModeler(EnsembleModeler):
    def __init__(self) -> None:
        super().__init__([
            knowledge_model.load('version_of_k_model'),
            generalizer.load('version_of_gen')
        ])

    def generate_training_data(self):
        
