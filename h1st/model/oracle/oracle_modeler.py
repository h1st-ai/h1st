import logging
from subprocess import call
from typing import Any, Dict, List, Union

import sklearn
import pandas as pd

from h1st.model.fuzzy.fuzzy_model import FuzzyModel
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.modeler import Modeler
from h1st.model.oracle.ensemble import MajorityVotingEnsemble
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.student import (
    RandomForestModeler,
    LogisticRegressionModeler,
)
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: ensemble for now just MajorityVotingEnsemble. as v1


# TODO: ensemble for now just MajorityVotingEnsemble. as v1


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
        inject_x_in_ensembler: bool = False,
    ) -> Oracle:
        """
        Build the components of Oracle, which are students and ensemblers.
        student is always MLModel and ensembler can be MLModel or RuleBasedModel.

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
        self.stats["inject_x_in_ensembler"] = inject_x_in_ensembler

        # Generate teacher's prediction which will be used as y value of students'
        # training data.
        teacher_predictons = self.model_class.generate_teacher_predictions(
            {"x": data["unlabeled_data"]}, teacher, self.stats
        )

        self.stats["labels"] = [col for col in teacher_predictons]

        # If teacher is FuzzyModel, convert float to zero or one to use this as y value.
        if isinstance(teacher, FuzzyModel) or issubclass(teacher.__class__, FuzzyModel):
            for key, val in fuzzy_thresholds.items():
                teacher_predictons[key] = list(
                    map(lambda y: 1 if y > val else 0, teacher_predictons[key])
                )

        # Build one binary classifier (from each student modeler) per label of teacher output.
        # If there are N number of student_modelers and M number of teacher output labels,
        # then, the total number of student models is N * M.
        students = {}
        for col in teacher_predictons:
            sub_train_data = {"x": data["unlabeled_data"], "y": teacher_predictons[col]}
            students[col] = [
                student_modeler.build_model(sub_train_data)
                for student_modeler in student_modelers
            ]

        # If there is labeled_data and ensembler_modeler is MLModeler,
        # then prepare the training data of ensembler.
        labeled_data = data.get("labeled_data", None)
        if isinstance(ensembler_modeler, MLModeler) and labeled_data is None:
            raise ValueError("No data to train the machine-learning-based ensembler")
        ensembler_data = {}
        if labeled_data:
            x_train_input = {"x": labeled_data["x_train"]}
            x_test_input = {"x": labeled_data["x_test"]}

            # Generate teacher predictions
            teacher_predictons_train = self.model_class.generate_teacher_predictions(
                x_train_input, teacher, self.stats
            )
            teacher_predictons_test = self.model_class.generate_teacher_predictions(
                x_test_input, teacher, self.stats
            )

            for col in teacher_predictons_train:

                # Generate student predictions
                student_preds_train_data = []
                student_preds_test_data = []
                for idx, student in enumerate(students[col]):
                    predict_proba = getattr(student, "predict_proba", None)
                    if callable(predict_proba) and isinstance(
                        ensembler_modeler, MLModeler
                    ):
                        s_pred_train = predict_proba(x_train_input)["predictions"][:, 0]
                        s_pred_test = predict_proba(x_test_input)["predictions"][:, 0]
                    else:
                        s_pred_train = student.predict(x_train_input)["predictions"]
                        s_pred_test = student.predict(x_test_input)["predictions"]
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

                # Create training data of ensembler
                ensembler_train_input = [
                    teacher_predictons_train[col]
                ] + student_preds_train_data
                ensembler_test_input = [
                    teacher_predictons_test[col]
                ] + student_preds_test_data

                # Inject original x value into input feature of Ensembler
                if (
                    isinstance(ensembler_modeler, MLModeler)
                    and (
                        isinstance(x_train_input["x"], pd.DataFrame)
                        or isinstance(x_train_input["x"], pd.Series)
                    )
                    and inject_x_in_ensembler
                ):
                    ensembler_train_input += [x_train_input["x"].reset_index(drop=True)]
                    ensembler_test_input += [x_test_input["x"].reset_index(drop=True)]

                ensembler_data[col] = {
                    "x_train": pd.concat(ensembler_train_input, axis=1).values,
                    "y_train": labeled_data["y_train"][col].reset_index(drop=True)
                    if isinstance(labeled_data["y_train"], pd.DataFrame)
                    else labeled_data["y_train"],
                    "x_test": pd.concat(ensembler_test_input, axis=1).values,
                    "y_test": labeled_data["y_test"][col].reset_index(drop=True)
                    if isinstance(labeled_data["y_test"], pd.DataFrame)
                    else labeled_data["y_test"],
                }
        else:
            ensembler_data = {key: None for key in teacher_predictons}

        # Build one ensemble per label of teacher output (M labels).
        # There will be M ensemblers in total.
        ensemblers = {}
        for col in ensembler_data:
            # print(ensembler_data[col]["x_train"])
            ensemblers[col] = ensembler_modeler.build_model(
                ensembler_data.get(col, None)
            )

        # Create Oracle model.
        oracle = self.model_class(teacher, students, ensemblers)

        # Pass modeler stats to model.
        if self.stats is not None:
            oracle.stats.update(self.stats.copy())

        # Generate metrics of all sub models (teacher, student, ensembler).
        if labeled_data:
            test_data = {"x": labeled_data["x_test"], "y": labeled_data["y_test"]}
            try:
                # Copy the metrics into metrics property of oracle
                oracle.metrics = self.evaluate_model(test_data, oracle)
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
        return oracle

    def evaluate_model(self, input_data: Dict, model: Oracle) -> Dict:
        if not hasattr(model, "students"):
            raise RuntimeError("No student built")

        teacher_pred = model.__class__.generate_teacher_predictions(
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

        # Generate the following metrics for each label.
        # Generate the metrics of all sub models (student, teacher, ensembler)
        evals = {}
        for metrics in ["f1_score", "precision", "recall"]:
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
                if (
                    isinstance(model.ensemblers[col], MLModel)
                    and (
                        isinstance(input_data["x"], pd.DataFrame)
                        or isinstance(input_data["x"], pd.Series)
                    )
                    and self.stats["inject_x_in_ensembler"]
                ):
                    ensembler_input += [input_data["x"].reset_index(drop=True)]
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
        elif metrics == "precision":
            return round(sklearn.metrics.precision_score(y_true, y_pred), 5)
        elif metrics == "recall":
            return round(sklearn.metrics.recall_score(y_true, y_pred), 5)
        elif metrics == "f1_score":
            return round(sklearn.metrics.f1_score(y_true, y_pred), 5)
        else:
            raise ValueError(f"Provided unsupported metrics type {metrics}")
