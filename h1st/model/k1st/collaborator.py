import logging

import pandas as pd

from h1st.model.wrapper.multi_model import MultiModel
from h1st.model.ml_model import MLModel


class kCollaboratorModel(MultiModel):

    name: str='k-Collaborator'
    data_key = 'X'
    output_key = 'predictions'

    def __init__(self):
        '''
        Model for running predictions with multiple models and combining the outputs.
        Also handles persistance and loading of submodels

        knowledge and ml models must take that same input and output a dict
        with the "predictions" key and value as list of dict or dict (matching
        the input format with key "X")
        i.e. model.predict({"X": {'k1': 12, 'k2': 22}}) ->
            {"predictions": {'output': 10}}
        '''
        super().__init__()
        self.ensemble = None

    def predict(self, input_data: dict) -> dict:
        submodel_out = super().predict(input_data)[self.output_key]

        # Inject original x value into input feature of Ensembler
        if (
                isinstance(self.ensemble, MLModel)
            and (
                isinstance(input_data["x"], pd.DataFrame)
                or isinstance(input_data["x"], pd.Series)
            )
            and self.stats["inject_x_in_ensembler"]
        ):
            submodel_out = pd.concat([submodel_out, input_data['x']], axis=1)

        if self.ensemble is None:
            return {self.output_key: submodel_out}

        ensemble_input = {'X': submodel_out}
        ensemble_key = getattr(self.ensemble, 'output_key', 'predictions')
        ensemble_pred = self.ensemble.predict(ensemble_input)[ensemble_key]
        return {self.output_key: ensemble_pred}

    def persist(self, version=None):
        ensemble_version = self.ensemble.persist()
        self.stats['ensemble'] = {
            'version': ensemble_version,
            'model_class': self.ensemble.__class__
        }

        version = super().persist(version)
        return version

    def load(self, version=None):
        super().load(version)

        ensemble_version = self.stats['ensemble']['version']
        ensemble_class = self.stats['ensemble']['model_class']
        self.ensemble = ensemble_class().load(ensemble_version)
        return self

