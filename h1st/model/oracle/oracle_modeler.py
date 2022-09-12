import logging
from subprocess import call
from typing import Any, Dict, List, Union

import sklearn
import pandas as pd

from h1st.model.fuzzy.fuzzy_model import FuzzyModel
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.modeler import Modeler
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.student import (
    RandomForestModeler,
    LogisticRegressionModeler,
)
from h1st.model.oracle.ensemble import MajorityVotingEnsemble
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OracleModeler(Modeler):
    def __init__(self, model_class=Oracle):
        self.model_class = model_class
        self.stats = {}

    def build_model(
        self,
        data: Dict[str, Any],
        teacher: RuleBasedModel,
        student_modelers: Union[List[MLModeler], MLModeler] = [
            RandomForestModeler(),
            LogisticRegressionModeler(),
        ],
        ensembler_modeler: Modeler = RuleBasedModeler(MajorityVotingEnsemble),
        features: List = None,
        fuzzy_thresholds: dict = None,
    ) -> Oracle:
        """
        Build the student and ensemble components.
        :param data: Unlabeled data.
        """
        if isinstance(teacher, FuzzyModel) and fuzzy_thresholds is None:
            raise ValueError(
                (
                    "If teacher model is FuzzyModel, "
                    "fuzzy_thresholds should be provided."
                )
            )

        if isinstance(student_modelers, MLModeler):
            student_modelers = [student_modelers]

        if not all(
            [
                isinstance(student_modeler, MLModeler)
                for student_modeler in student_modelers
            ]
        ):
            raise ValueError(("All student modelers should be MLModeler."))

        self.stats["fuzzy_thresholds"] = fuzzy_thresholds
        self.stats["features"] = features

        # Generate features to get students' predictions
        teacher_predictons = self.model_class.generate_teacher_prediction(
            {"x": data["unlabeled_data"]}, teacher, self.stats
        )
        self.stats["labels"] = [col for col in teacher_predictons]

        if isinstance(teacher, FuzzyModel):
            for key, val in fuzzy_thresholds.items():
                teacher_predictons[key] = list(
                    map(lambda y: 1 if y > val else 0, teacher_predictons[key])
                )

        # Build one binary classifier per class of teacher output
        students = {}
        for col in teacher_predictons:
            sub_train_data = {"x": data["unlabeled_data"], "y": teacher_predictons[col]}
            students[col] = [
                student_modeler.build_model(sub_train_data)
                for student_modeler in student_modelers
            ]

        # Build one ensemble per class of teacher output
        # Train the ensembler
        labeled_data = data.get("labeled_data", None)

        if isinstance(ensembler_modeler, MLModeler) and labeled_data is None:
            raise ValueError("No data to train the machine-learning-based ensembler")

        ensembler_data = {}
        if labeled_data:
            teacher_predictons_train = self.model_class.generate_teacher_prediction(
                {"x": labeled_data["x_train"]}, teacher, self.stats
            )
            teacher_predictons_test = self.model_class.generate_teacher_prediction(
                {"x": labeled_data["x_test"]}, teacher, self.stats
            )

            # should update here to create
            for col in teacher_predictons_train:
                ensembler_sub_train_data = {
                    "x": labeled_data["x_train"],
                    "y": teacher_predictons_train[col],
                }
                ensembler_sub_test_data = {
                    "x": labeled_data["x_test"],
                    "y": teacher_predictons_test[col],
                }

                student_preds_train_data = []
                student_preds_test_data = []
                for idx, student in enumerate(students[col]):
                    predict_proba = getattr(student, "predict_proba", None)
                    if callable(predict_proba) and isinstance(
                        ensembler_modeler, MLModeler
                    ):
                        s_pred_train = predict_proba(ensembler_sub_train_data)[
                            "predictions"
                        ][:, 0]
                        s_pred_test = predict_proba(ensembler_sub_test_data)[
                            "predictions"
                        ][:, 0]
                    else:
                        s_pred_train = student.predict(ensembler_sub_train_data)[
                            "predictions"
                        ]
                        s_pred_test = student.predict(ensembler_sub_test_data)[
                            "predictions"
                        ]
                    student_preds_train_data.append(
                        pd.Series(
                            s_pred_train,
                            name=f"stud_{idx}_{col}",
                        )
                    )
                    student_preds_test_data.append(
                        pd.Series(
                            s_pred_test,
                            name=f"stud_{idx}_{col}",
                        ),
                    )

                ensembler_train_input = [
                    teacher_predictons_train[col]
                ] + student_preds_train_data
                ensembler_test_input = [
                    teacher_predictons_test[col]
                ] + student_preds_test_data

                if isinstance(ensembler_modeler, MLModeler) and (
                    isinstance(ensembler_sub_train_data["x"], pd.DataFrame)
                    or isinstance(ensembler_sub_train_data["x"], pd.Series)
                ):
                    ensembler_train_input += [ensembler_sub_train_data["x"]]
                    ensembler_test_input += [ensembler_sub_test_data["x"]]

                ensembler_data[col] = {
                    "x_train": pd.concat(ensembler_train_input, axis=1).values,
                    "y_train": labeled_data["y_train"][col]
                    if isinstance(labeled_data["y_train"], pd.DataFrame)
                    else labeled_data["y_train"],
                    "x_test": pd.concat(ensembler_test_input, axis=1).values,
                    "y_test": labeled_data["y_test"][col]
                    if isinstance(labeled_data["y_test"], pd.DataFrame)
                    else labeled_data["y_test"],
                }
        else:
            ensembler_data = {key: None for key in teacher_predictons}

        ensemblers = {}
        for col in ensembler_data:
            ensemblers[col] = ensembler_modeler.build_model(
                ensembler_data.get(col, None)
            )

        oracle = self.model_class.construct_oracle(teacher, students, ensemblers)

        # Pass stats to the model
        if self.stats is not None:
            oracle.stats.update(self.stats.copy())

        # Generate metrics
        if labeled_data:
            test_data = {"x": labeled_data["x_test"], "y": labeled_data["y_test"]}
            try:
                oracle.metrics = self.evaluate_model(test_data, oracle)
            except:
                logging.error("Couldn't complete the submodel evaluation.")
            else:
                logging.info("Evaluated all sub models successfully.")
        return oracle

    def evaluate_model(self, input_data: Dict, model: Oracle) -> Dict:
        if not hasattr(model, "students"):
            raise RuntimeError("No student built")

        teacher_pred = model.__class__.generate_teacher_prediction(
            input_data, model.teacher, model.stats
        )
        teacher_pred_one_hot = {}
        if isinstance(model.teacher, FuzzyModel):
            for key, val in model.stats["fuzzy_thresholds"].items():
                teacher_pred_one_hot[key] = list(
                    map(lambda y: 1 if y > val else 0, teacher_pred[key])
                )
        else:
            teacher_pred_one_hot = teacher_pred

        evals = {}
        for metrics in ["accuracy", "f1_score"]:
            temp = {}
            for col in teacher_pred:
                student_preds_one_hot = [
                    pd.Series(
                        student.predict(input_data)["predictions"],
                        name=f"stud_{idx}_{col}",
                    )
                    for idx, student in enumerate(model.students[col])
                ]
                student_preds = []
                for idx, student in enumerate(model.students[col]):
                    predict_proba = getattr(student, "predict_proba", None)
                    if callable(predict_proba) and isinstance(
                        model.ensemblers[col], MLModel
                    ):
                        s_pred = predict_proba(input_data)["predictions"][:, 0]
                    else:
                        s_pred = student.predict(input_data)["predictions"]
                    student_preds.append(
                        pd.Series(
                            s_pred,
                            name=f"stud_{idx}_{col}",
                        )
                    )

                ensembler_input = [teacher_pred[col]] + student_preds
                if isinstance(model.ensemblers[col], MLModel) and (
                    isinstance(input_data["x"], pd.DataFrame)
                    or isinstance(input_data["x"], pd.Series)
                ):
                    ensembler_input += [input_data["x"]]
                    ensembler_input = pd.concat(ensembler_input, axis=1).values
                else:
                    ensembler_input = pd.concat(ensembler_input, axis=1)

                ensemblers_pred = model.ensemblers[col].predict({"x": ensembler_input})[
                    "predictions"
                ]
                y_true = input_data["y"][col]

                temp[col] = {
                    "teacher": self.get_metrics_score(
                        y_true, teacher_pred_one_hot[col], metrics
                    ),
                    "students": [
                        self.get_metrics_score(y_true, student_pred, metrics)
                        for student_pred in student_preds_one_hot
                    ],
                    "ensemblers": self.get_metrics_score(
                        y_true, ensemblers_pred, metrics
                    ),
                }
            evals[metrics] = temp
        return evals

    def get_metrics_score(
        self, y_true: List[int], y_pred: List[int], metrics: str
    ) -> float:
        if metrics == "accuracy":
            return round(sklearn.metrics.accuracy_score(y_true, y_pred), 5)
        elif metrics == "f1_score":
            return round(sklearn.metrics.f1_score(y_true, y_pred), 5)
        else:
            raise ValueError(f"Provided unsupported metrics type {metrics}")
