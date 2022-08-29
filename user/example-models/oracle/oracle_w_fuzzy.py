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
    vars = FuzzyVariables()
    vars.add(
        var_name="sepal_length",
        var_type="antecedent",
        var_range=np.arange(
            meta_data["sepal_length"]["min"], meta_data["sepal_length"]["max"], 0.1
        ),
        membership_funcs=[
            ("small", fm.GAUSSIAN, [5, 1]),
            ("large", fm.TRIANGLE, [6, 6.4, 8]),
        ],
    )
    vars.add(
        var_name="sepal_width",
        var_type="antecedent",
        var_range=np.arange(
            meta_data["sepal_width"]["min"], meta_data["sepal_width"]["max"], 0.1
        ),
        membership_funcs=[
            ("small", fm.GAUSSIAN, [2.8, 0.3]),
            ("large", fm.GAUSSIAN, [3.3, 0.5]),
        ],
    )
    vars.add(
        var_name="setosa",
        var_type="consequent",
        var_range=np.arange(0, 1 + 1e-5, 0.1),
        membership_funcs=[
            ("false", fm.GAUSSIAN, [0, 0.4]),
            ("true", fm.GAUSSIAN, [1, 0.4]),
        ],
    )

    rules = FuzzyRules()
    rules.add(
        "rule1",
        if_term=vars.get("sepal_length")["small"] & vars.get("sepal_width")["large"],
        then_term=vars.get("setosa")["false"],
    )
    rules.add(
        "rule2",
        if_term=vars.get("sepal_length")["large"] & vars.get("sepal_width")["small"],
        then_term=vars.get("setosa")["true"],
    )

    modeler = FuzzyModeler()
    model = modeler.build_model(vars, rules)
    return model


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

    return {
        "unlabeled_data": training_data[["sepal_length", "sepal_width"]],
        "labeled_data": {
            "x_train": training_data[["sepal_length", "sepal_width"]],
            "y_train": training_data["species"],
            "x_test": test_data[["sepal_length", "sepal_width"]],
            "y_test": test_data["species"],
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
    meta_data = get_meta_data(data)
    fuzzy_teacher = build_iris_fuzzy_model(meta_data)
    input_vars = {"sepal_length": 5, "sepal_width": 3.7}

    modeler = OracleModeler()
    fuzzy_thresholds = {"setosa": 0.6}
    # new_data = {"unlabeled_data": data["training_data"]["x"]}

    oracle = modeler.build_model(
        data=data, teacher=fuzzy_teacher, fuzzy_thresholds=fuzzy_thresholds
    )

    print(oracle.metrics)
