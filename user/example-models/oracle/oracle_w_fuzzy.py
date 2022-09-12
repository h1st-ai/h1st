import imp
import os
import tempfile

import numpy as np
import pandas as pd
from sklearn import datasets, metrics


from h1st.model.fuzzy import (
    FuzzyModeler,
    FuzzyRules,
    FuzzyVariables,
    FuzzyMembership as fm,
)
from h1st.model.oracle import OracleModeler


def build_iris_fuzzy_model(meta_data):
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

    modeler = FuzzyModeler()
    model = modeler.build_model(fuzzy_vars, fuzzy_rule)
    return model


def load_data():
    df_raw = datasets.load_iris(as_frame=True).frame
    df_raw.columns = [
        "sepal_length",
        "sepal_width",
        "petal_length",
        "petal_width",
        "setosa",
    ]
    df_raw["setosa"] = df_raw["setosa"].apply(lambda x: 1 if x == 0 else 0)

    # randomly split training and testing dataset
    example_test_data_ratio = 0.4
    df_raw = df_raw.sample(frac=1, random_state=7).reset_index(drop=True)
    n = df_raw.shape[0]
    n_test = int(n * example_test_data_ratio)
    training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
    test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)

    return {
        "unlabeled_data": training_data[["sepal_length", "sepal_width"]],
        "labeled_data": {
            "x_train": training_data[["sepal_length", "sepal_width"]],
            "y_train": training_data[["setosa"]],
            "x_test": test_data[["sepal_length", "sepal_width"]],
            "y_test": test_data[["setosa"]],
        },
    }

    # return {
    #     "training_data": {
    #         "x": training_data[["sepal_length", "sepal_width"]],
    #         "y": training_data["species"],
    #     },
    #     "test_data": {
    #         "x": test_data[["sepal_length", "sepal_width"]],
    #         "y": test_data["species"],
    #     },
    # }


def get_meta_data(data):
    res = {}
    for k, v in data["labeled_data"]["x_train"].max().to_dict().items():
        res[k] = {"max": v}
    for k, v in data["labeled_data"]["x_train"].min().to_dict().items():
        res[k].update({"min": v})
    return res


if __name__ == "__main__":
    data = load_data()
    # data["labeled_data"]["y_train"].rename(columns={"species": "setosa"}, inplace=True)
    # data["labeled_data"]["y_test"].rename(columns={"species": "setosa"}, inplace=True)

    meta_data = get_meta_data(data)
    fuzzy_teacher = build_iris_fuzzy_model(meta_data)
    fuzzy_thresholds = {"setosa": 0.6}
    modeler = OracleModeler()
    oracle = modeler.build_model(
        data=data, teacher=fuzzy_teacher, fuzzy_thresholds=fuzzy_thresholds
    )
    print(oracle.metrics)
