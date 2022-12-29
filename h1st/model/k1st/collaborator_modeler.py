import logging

import pandas as pd

from h1st.model.wrapper.multi_modeler import MultiModeler
from h1st.model.oracle.ensemble import MajorityVotingEnsemble
from h1st.model.rule_based_modeler import RuleBasedModeler
from h1st.model.k1st.collaborator import kCollaboratorModel


class kCollaboratorModeler(MultiModeler):

    model_class = kCollaboratorModel

    def __init__(self):
        super().__init__()

    def build_model(self, prepared_data: dict,
                    modelers: list['h1st.MLModeler']=[],
                    ensemble_modeler: 'h1st.Modeler' = RuleBasedModeler(MajorityVotingEnsemble),
                    models: list['h1st.PredictiveModel']=None,
                    inject_x_in_ensembler: bool=False) -> 'BaseOracle':
        '''
        prepared_data must be in the format necessary for modelers
        '''
        self.stats['inject_x_in_ensembler'] = inject_x_in_ensembler
        model = super().build_model(prepared_data, modelers)
        for i, m in enumerate(models):
            model.add_model(m, name=f'prebuilt-{model.__class__.__name__}-{i}')

        # train ensemble
        raw_pred = model.predict(
            {model.data_key: prepared_data['x_train']}
        )[model.output_key]

        # If there is labeled_data and ensembler_modeler is MLModeler,
        # then prepare the training data of ensembler.
        labeled_data = prepared_data.get("labeled_data", None)
        if isinstance(ensembler_modeler, MLModeler) and labeled_data is None:
            raise ValueError("No data to train the machine-learning-based ensembler")

        ensembler_data = {}
        if labeled_data:
            x_train_input = {"x": labeled_data["x_train"]}
            x_test_input = {"x": labeled_data["x_test"]}

            ensembler_train_input = model.predict({
                model.data_key: x_train_input
            })[model.output_key]

            ensembler_test_input = model.predict({
                model.data_key: x_test_input
            })

            ensembler_data = {
                'x_train': ensembler_train_input,
                'y_train': labeled_data['y_train'],
                'x_test': ensembler_test_input,
                'y_test': labeled_data['y_test']
            }
        else:
            ensembler_data = None

        ensemble = ensemble_modeler.build_model(ensembler_data)
        model.ensemble = ensemble

        # Generate metrics of all sub models (teacher, student, ensembler).
        if labeled_data:
            test_data = {"x": labeled_data["x_test"], "y": labeled_data["y_test"]}
            try:
                model.metrics = self.evaluate_model(test_data, model)
            except Exception as e:
                logging.error(
                    (
                        "Couldn't complete the submodel evaluation. "
                        "Got the following error."
                    )
                )
                logging.error(e)
            else:
                logging.info("Evaluated all sub models successfully.")

        return model

    def evaluate_model(self, test_data: dict, model: Model):
        submodel_metrics = super().evaluate_model()
        metrics = {'submodel_metrics': submodel_metrics}
        # TODO: Compute overall model metrics
        return metrics

