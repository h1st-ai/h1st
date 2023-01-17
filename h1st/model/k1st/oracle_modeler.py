import logging
from typing import List

from h1st.model.wrapper.multi_modeler import MultiModeler
from h1st.model.oracle.ensembler_models import MajorityVotingEnsembleModel
from h1st.model.rule_based_modeler import RuleBasedModeler
from h1st.model.k1st.oracle import kOracleModel
from h1st.model.predictive_model import PredictiveModel
from h1st.model.modeler import Modeler
from h1st.model.model import Model
from h1st.model.ml_modeler import MLModeler


class kOracleModeler(MultiModeler):

    model_class = kOracleModel

    def __init__(self):
        super().__init__()

    def build_model(
        self,
        prepared_data: dict,
        modelers: List[MLModeler] = [],
        ensemble_modeler: Modeler = RuleBasedModeler(MajorityVotingEnsembleModel),
        teacher: PredictiveModel = None,
        inject_x_in_ensembler: bool = False,
    ) -> kOracleModel:
        '''
        prepared_data must be in the format necessary for modelers
        '''
        if prepared_data is None:
            model = kOracleModel()
            model.add_model(teacher, f'prebuilt-{teacher.__class__.__name__}')
            model.stats['input_features'] = teacher.stats['input_features']
            return model

        teacher_data_key = getattr(teacher, 'data_key', 'X')
        teacher_output_key = getattr(teacher, 'output_key', 'predictions')
        teacher_pred = teacher.predict({teacher_data_key: prepared_data['X_teacher_train']})[
            teacher_output_key
        ]
        student_training_data = prepared_data.copy()
        student_training_data['y_train'] = teacher_pred
        if 'X_test' in prepared_data.keys():
            student_training_data['y_test'] = teacher.predict(
                {teacher_data_key: prepared_data['X_test']}
            )[teacher_output_key]

        self.stats['inject_x_in_ensembler'] = inject_x_in_ensembler
        model = super().build_model(student_training_data, modelers)

        # Add teacher to MultiModel
        model.add_model(teacher, f'prebuilt-{teacher.__class__.__name__}')

        # train ensemble
        raw_pred = model.predict({model.data_key: prepared_data['X_train']})[
            model.output_key
        ]

        # If there is labeled_data and ensembler_modeler is MLModeler,
        # then prepare the training data of ensembler.
        labeled_data = prepared_data.get("labeled_data", None)
        if isinstance(ensemble_modeler, MLModeler) and labeled_data is None:
            raise ValueError("No data to train the machine-learning-based ensembler")

        ensembler_data = {}
        if labeled_data:
            x_train_input = {"X": labeled_data["X_train"]}
            x_test_input = {"X": labeled_data["X_test"]}

            ensembler_train_input = model.predict({model.data_key: x_train_input})[
                model.output_key
            ]

            ensembler_test_input = model.predict({model.data_key: x_test_input})

            ensembler_data = {
                'X_train': ensembler_train_input,
                'y_train': labeled_data['y_train'],
                'X_test': ensembler_test_input,
                'y_test': labeled_data['y_test'],
            }
        else:
            ensembler_data = None

        ensemble = ensemble_modeler.build_model(ensembler_data)
        model.ensemble = ensemble

        # Generate metrics of all sub models (teacher, student, ensembler).
        if labeled_data:
            test_data = {"X": labeled_data["X_test"], "y": labeled_data["y_test"]}
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

        model.stats['input_features'] = list(prepared_data['X_train'].columns)

        return model

    def evaluate_model(self, test_data: dict, model: Model):
        submodel_metrics = super().evaluate_model(test_data, model)
        metrics = {'submodel_metrics': submodel_metrics}
        # TODO: Compute overall model metrics
        return metrics
