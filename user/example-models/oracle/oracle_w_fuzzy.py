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
    FuzzyMembership as fm
)
from h1st.model.oracle import OracleModeler


def build_iris_fuzzy_model(meta_data):
    fuzzy_vars = FuzzyVariables()
    fuzzy_vars.add(
        var_name='sepal_length',
        var_type='antecedent',
        var_range=np.arange(
            meta_data['sepal_length']['min'], 
            meta_data['sepal_length']['max'], 
            0.1
        ),
        membership_funcs=[('small', fm.GAUSSIAN, [5, 1]),
                            ('large', fm.TRIANGLE, [6, 6.4, 8])]
    )
    fuzzy_vars.add(
        var_name='sepal_width',
        var_type='antecedent',
        var_range=np.arange(
            meta_data['sepal_width']['min'], 
            meta_data['sepal_width']['max'], 
            0.1
        ),
        membership_funcs=[('small', fm.GAUSSIAN, [2.8, 0.3]),
                          ('large', fm.GAUSSIAN, [3.3, 0.5])]
    )
    fuzzy_vars.add(
        var_name='setosa',
        var_type='consequent',
        var_range=np.arange(0, 1+1e-5, 0.1),
        membership_funcs=[('false', fm.GAUSSIAN, [0, 0.4]),
                          ('true', fm.GAUSSIAN, [1, 0.4])]
    )
    
    fuzzy_rule = FuzzyRules()
    fuzzy_rule.add(
        'rule1',
        if_=fuzzy_vars.sepal_length['small'] & fuzzy_vars.sepal_width['large'],
        then_=fuzzy_vars.setosa['false']
    )
    fuzzy_rule.add(
        'rule2',
        if_=fuzzy_vars.sepal_length['large'] & fuzzy_vars.sepal_width['small'],
        then_=fuzzy_vars.setosa['true']
    )
    
    modeler = FuzzyModeler()
    model = modeler.build_model(fuzzy_rule)
    return model


def load_data():
    df_raw = datasets.load_iris(as_frame=True).frame
    df_raw.columns = ['sepal_length','sepal_width','petal_length','petal_width', 'species']
    df_raw['species'] = df_raw['species'].apply(lambda x: 1 if x==0 else 0)

    # randomly split training and testing dataset
    example_test_data_ratio = 0.4
    df_raw = df_raw.sample(frac=1, random_state=7).reset_index(drop=True)
    n = df_raw.shape[0]
    n_test = int(n * example_test_data_ratio)
    training_data = df_raw.iloc[n_test:, :].reset_index(drop=True)
    test_data = df_raw.iloc[:n_test, :].reset_index(drop=True)

    return {
        'training_data': {
            'X': training_data[['sepal_length', 'sepal_width']],
            'y': training_data['species']
        },
        'test_data': {
            'X': test_data[['sepal_length', 'sepal_width']],
            'y': test_data['species']
        },
    }


def build_oracle():
    fuzzy_teacher = build_iris_fuzzy_model()
    data = load_data()

    modeler = OracleModeler()
    oracle = modeler.build_model(
        data=data,
        teacher=fuzzy_teacher
    )
    return oracle


def get_meta_data(data):
    res = {}
    for k, v in data['training_data']['X'].max().to_dict().items():
        res[k] = {'max': v}
    for k, v in data['training_data']['X'].min().to_dict().items():
        res[k].update({'min': v})    
    return res

def evaluate_model(model, data):
    X, y_true = data['X_test'], data['y_test']
    y_pred = pd.Series(model.predict({'X': X})['predictions'])
    return {'r2_score': metrics.r2_score(y_true, y_pred)}

if __name__ == "__main__":
    data = load_data()
    meta_data = get_meta_data(data)
    fuzzy_model = build_iris_fuzzy_model(meta_data)
    input_vars = {
        'sepal_length': 5,
        'sepal_width': 3.7
    }
    result = fuzzy_model.predict(input_vars)
    print(result)
    # oracle = build_oracle()
    # input_vars = {
    #         'var1': 7,
    #         'var2': 10
    # }
    
    # # Run prediction of Fuzzy Model.
    # prediction = oracle.predict(input_vars)
    # print("prediction['conclusion1']: ", prediction['conclusion1'])

    # # Persist Fuzzy Model.
    # with tempfile.TemporaryDirectory() as path:
    #     os.environ['H1ST_MODEL_REPO_PATH'] = path
    #     fuzzy_model.persist('my_version_1')

    #     # Load Fuzzy Model.
    #     reloaded_fuzzy_model = FuzzyModel().load('my_version_1')

    # prediction = reloaded_fuzzy_model.predict(input_vars)
    # print("prediction['conclusion1']: ", prediction['conclusion1'])

