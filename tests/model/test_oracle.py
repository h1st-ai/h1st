from operator import imod
import os
import tempfile
from typing import Any, Dict

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn import datasets, metrics
import numpy as np

from h1st.model.predictive_model import PredictiveModel
from h1st.model.ml_model import MLModel
from h1st.model.ml_modeler import MLModeler
from h1st.model.oracle.oracle import Oracle
from h1st.model.oracle.oracle_modeler import OracleModeler
from h1st.model.oracle.student import LogisticRegressionModeler, RandomForestModeler
from h1st.model.oracle.ensemble import MajorityVotingEnsemble, MLPEnsembleModeler
from h1st.model.rule_based_model import RuleBasedModel
from h1st.model.rule_based_modeler import RuleBasedModeler


class RuleModel(RuleBasedModel):
    sepal_length_max: float = 6.0
    sepal_length_min: float = 4.0
    sepal_width_min: float = 2.8
    sepal_width_max: float = 4.6

    def predict(self, data):
        df = data["x"]
        return {
            "predictions": pd.DataFrame(
                map(self.predict_setosa, df["sepal_length"], df["sepal_width"]),
                columns=["setosa"],
            )
        }

    def predict_setosa(self, sepal_length, sepal_width):
        return (
            1
            if (self.sepal_length_min <= sepal_length <= self.sepal_length_max)
            & (self.sepal_width_min <= sepal_width <= self.sepal_width_max)
            else 0
        )


def build_fuzzy_model(data):
    from h1st.model.fuzzy import (
        FuzzyVariables,
        FuzzyMembership as fm,
        FuzzyRules,
        FuzzyModeler,
    )

    def get_meta_data(data):
        res = {}
        for k, v in data["training_data"]["x"].max().to_dict().items():
            res[k] = {"max": v}
        for k, v in data["training_data"]["x"].min().to_dict().items():
            res[k].update({"min": v})
        return res

    meta_data = get_meta_data(data)
    fuzzy_vars = FuzzyVariables()
    fuzzy_vars.add(
        var_name="sepal_length",
        var_type="antecedent",
        var_range=np.arange(
            meta_data["sepal_length"]["min"], meta_data["sepal_length"]["max"], 0.1
        ),
        membership_funcs=[
            ("small", fm.GAUSSIAN, [5, 0.7]),
            ("large", fm.TRAPEZOID, [5.8, 6.4, 8, 8]),
        ],
    )
    fuzzy_vars.add(
        var_name="sepal_width",
        var_type="antecedent",
        var_range=np.arange(
            meta_data["sepal_width"]["min"], meta_data["sepal_width"]["max"], 0.1
        ),
        membership_funcs=[
            ("small", fm.GAUSSIAN, [2.8, 0.15]),
            ("large", fm.GAUSSIAN, [3.3, 0.25]),
        ],
    )
    fuzzy_vars.add(
        var_name="setosa",
        var_type="consequent",
        var_range=np.arange(0, 1 + 1e-5, 0.1),
        membership_funcs=[
            ("false", fm.GAUSSIAN, [0, 0.4]),
            ("true", fm.GAUSSIAN, [1, 0.4]),
        ],
    )
    fuzzy_vars.add(
        var_name="non_setosa",
        var_type="consequent",
        var_range=np.arange(0, 1 + 1e-5, 0.1),
        membership_funcs=[
            ("false", fm.GAUSSIAN, [0, 0.4]),
            ("true", fm.GAUSSIAN, [1, 0.4]),
        ],
    )

    fuzzy_rule = FuzzyRules()
    fuzzy_rule.add(
        "rule1",
        if_term=fuzzy_vars.get("sepal_length")["small"]
        & fuzzy_vars.get("sepal_width")["large"],
        then_term=fuzzy_vars.get("setosa")["true"],
    )
    fuzzy_rule.add(
        "rule2",
        if_term=fuzzy_vars.get("sepal_length")["large"]
        & fuzzy_vars.get("sepal_width")["small"],
        then_term=fuzzy_vars.get("setosa")["false"],
    )
    fuzzy_rule.add(
        "rule3",
        if_term=fuzzy_vars.get("sepal_length")["large"]
        & fuzzy_vars.get("sepal_width")["small"],
        then_term=fuzzy_vars.get("non_setosa")["true"],
    )
    fuzzy_rule.add(
        "rule4",
        if_term=fuzzy_vars.get("sepal_length")["small"]
        & fuzzy_vars.get("sepal_width")["large"],
        then_term=fuzzy_vars.get("non_setosa")["false"],
    )

    modeler = FuzzyModeler()
    return modeler.build_model(fuzzy_vars, fuzzy_rule)


def load_data():
    df_raw = datasets.load_iris(as_frame=True).frame
    df_raw.columns = [
        "sepal_length",
        "sepal_width",
        "petal_length",
        "petal_width",
        "species",
    ]
    df_raw["species"] = df_raw["species"].apply(lambda x: 1 if x == 0 else 0)

    # randomly split training and testing dataset
    example_test_data_ratio = 0.4
    df_raw = df_raw.sample(frac=1, random_state=7).reset_index(drop=True)
    n = df_raw.shape[0]
    n_test = int(n * example_test_data_ratio)
    training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
    test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)

    # make multi-label
    training_data_y = pd.concat(
        [
            training_data["species"].rename("setosa"),
            training_data["species"].apply(lambda x: x ^ 1).rename("non_setosa"),
        ],
        axis=1,
    )
    test_data_y = pd.concat(
        [
            test_data["species"].rename("setosa"),
            test_data["species"].apply(lambda x: x ^ 1).rename("non_setosa"),
        ],
        axis=1,
    )

    return {
        "training_data": {
            "x": training_data[["sepal_length", "sepal_width"]],
            "y": training_data_y,
        },
        "test_data": {
            "x": test_data[["sepal_length", "sepal_width"]],
            "y": test_data_y,
        },
    }


class TestOracle:
    def test_rule_based_ensemble_one_student(self):
        data = load_data()
        oracle_modeler = OracleModeler()
        oracle = oracle_modeler.build_model(
            data={"unlabeled_data": data["training_data"]["x"]},
            teacher=RuleModel(),
            student_modelers=RandomForestModeler(),
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsemble),
        )

        pred = oracle.predict(data["test_data"])["predictions"]
        assert len(pred["setosa"]) == len(data["test_data"]["y"])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ["H1ST_MODEL_REPO_PATH"] = path
            version = oracle.persist()

            oracle_2 = Oracle().load(version)

            assert "sklearn" in str(type(oracle_2.students["setosa"][0].base_model))
            pred_2 = oracle_2.predict(data["test_data"])["predictions"]
            pred_df = pd.DataFrame({"pred": pred["setosa"], "pred_2": pred_2["setosa"]})
            assert len(pred_df[pred_df["pred"] != pred_df["pred_2"]]) == 0

    def test_rule_based_ensemble_multiple_students(self):
        data = load_data()
        oracle_modeler = OracleModeler()
        oracle = oracle_modeler.build_model(
            data={"unlabeled_data": data["training_data"]["x"]},
            teacher=RuleModel(),
            student_modelers=[RandomForestModeler(), LogisticRegressionModeler()],
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsemble),
        )

        pred = oracle.predict(data["test_data"])["predictions"]
        assert len(pred["setosa"]) == len(data["test_data"]["y"])
        assert any(pred["setosa"] != data["test_data"]["y"])

        with tempfile.TemporaryDirectory() as path:
            os.environ["H1ST_MODEL_REPO_PATH"] = path
            version = oracle.persist()

            oracle_2 = Oracle().load(version)

            assert "sklearn" in str(type(oracle_2.students["setosa"][0].base_model))
            pred_2 = oracle_2.predict(data["test_data"])["predictions"]
            pred_df = pd.DataFrame({"pred": pred["setosa"], "pred_2": pred_2["setosa"]})
            assert len(pred_df[pred_df["pred"] != pred_df["pred_2"]]) == 0

    def test_ml_ensemble(self):
        data = load_data()
        new_data = {
            "unlabeled_data": data["training_data"]["x"],
            "labeled_data": {
                "x_train": data["training_data"]["x"],
                "y_train": data["training_data"]["y"],
                "x_test": data["test_data"]["x"],
                "y_test": data["test_data"]["y"],
            },
        }
        oracle_modeler = OracleModeler()
        oracle = oracle_modeler.build_model(
            data=new_data,
            teacher=RuleModel(),
            student_modelers=[RandomForestModeler(), LogisticRegressionModeler()],
            ensembler_modeler=MLPEnsembleModeler(),
        )

        pred = oracle.predict(data["test_data"])["predictions"]
        assert len(pred["setosa"]) == len(data["test_data"]["y"])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ["H1ST_MODEL_REPO_PATH"] = path
            version = oracle.persist()

            oracle_2 = Oracle().load(version)

            assert "sklearn" in str(type(oracle_2.students["setosa"][0].base_model))
            pred_2 = oracle_2.predict(data["test_data"])["predictions"]
            pred_df = pd.DataFrame({"pred": pred["setosa"], "pred_2": pred_2["setosa"]})
            assert len(pred_df[pred_df["pred"] != pred_df["pred_2"]]) == 0

    def test_rule_based_ensemble_fuzzy_teacher_multiple_students(self):
        data = load_data()
        fuzzy_model = build_fuzzy_model(data)
        oracle_modeler = OracleModeler()
        oracle = oracle_modeler.build_model(
            data={"unlabeled_data": data["training_data"]["x"]},
            teacher=fuzzy_model,
            fuzzy_thresholds={"setosa": 0.6, "non_setosa": 0.49},
            student_modelers=[RandomForestModeler(), LogisticRegressionModeler()],
            ensembler_modeler=RuleBasedModeler(MajorityVotingEnsemble),
        )

        pred = oracle.predict(data["test_data"])["predictions"]
        assert len(pred["setosa"]) == len(data["test_data"]["y"])
        assert any(pred["setosa"] != data["test_data"]["y"])

        with tempfile.TemporaryDirectory() as path:
            os.environ["H1ST_MODEL_REPO_PATH"] = path
            version = oracle.persist()

            oracle_2 = Oracle().load(version)

            assert "sklearn" in str(type(oracle_2.students["setosa"][0].base_model))
            pred_2 = oracle_2.predict(data["test_data"])["predictions"]
            pred_df = pd.DataFrame({"pred": pred["setosa"], "pred_2": pred_2["setosa"]})
            assert len(pred_df[pred_df["pred"] != pred_df["pred_2"]]) == 0

    def test_ml_ensemble_fuzzy_teacher(self):
        data = load_data()
        fuzzy_model = build_fuzzy_model(data)
        new_data = {
            "unlabeled_data": data["training_data"]["x"],
            "labeled_data": {
                "x_train": data["training_data"]["x"],
                "y_train": data["training_data"]["y"],
                "x_test": data["test_data"]["x"],
                "y_test": data["test_data"]["y"],
            },
        }
        oracle_modeler = OracleModeler()
        oracle = oracle_modeler.build_model(
            data=new_data,
            teacher=fuzzy_model,
            fuzzy_thresholds={"setosa": 0.6, "non_setosa": 0.49},
            student_modelers=[RandomForestModeler(), LogisticRegressionModeler()],
            ensembler_modeler=MLPEnsembleModeler(),
        )

        pred = oracle.predict(data["test_data"])["predictions"]
        assert len(pred["setosa"]) == len(data["test_data"]["y"])
        # print(metrics.f1_score(data['test_data']['y'], pred, average='macro'))

        with tempfile.TemporaryDirectory() as path:
            os.environ["H1ST_MODEL_REPO_PATH"] = path
            version = oracle.persist()

            oracle_2 = Oracle().load(version)

            assert "sklearn" in str(type(oracle_2.students["setosa"][0].base_model))
            pred_2 = oracle_2.predict(data["test_data"])["predictions"]
            pred_df = pd.DataFrame({"pred": pred["setosa"], "pred_2": pred_2["setosa"]})
            assert len(pred_df[pred_df["pred"] != pred_df["pred_2"]]) == 0
