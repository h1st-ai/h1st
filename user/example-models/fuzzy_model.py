import os
import tempfile

import numpy as np

from h1st.model.fuzzy import (
    FuzzyModeler,
    FuzzyModel,
    FuzzyMembership as fm,
    FuzzyVariables,
    FuzzyRules,
)


def build_fuzzy_model():
    vars = FuzzyVariables()
    vars.add(
        var_name='var1',
        var_type='antecedent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('normal', fm.GAUSSIAN, [3, 3.3]),
            ('abnormal', fm.TRIANGLE, [8, 15, 15]),
        ],
    )
    vars.add(
        var_name='var2',
        var_type='antecedent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('normal', fm.GAUSSIAN, [3, 3.3]),
            ('abnormal', fm.TRIANGLE, [8, 15, 15]),
        ],
    )
    vars.add(
        var_name='conclusion1',
        var_type='consequent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('no', fm.TRAPEZOID, [0, 0, 4, 6]),
            ('yes', fm.TRAPEZOID, [4, 6, 10, 10]),
        ],
    )

    rules = FuzzyRules()
    rules.add(
        rule_name='rule1',
        if_term=vars.get('var1')['abnormal'] & vars.get('var2')['abnormal'],
        then_term=vars.get('conclusion1')['yes'],
    )
    rules.add(
        rule_name='rule2',
        if_term=vars.get('var1')['normal'],
        then_term=vars.get('conclusion1')['no'],
    )
    rules.add(
        rule_name='rule3',
        if_term=vars.get('var2')['normal'],
        then_term=vars.get('conclusion1')['no'],
    )

    modeler = FuzzyModeler()
    model = modeler.build_model(vars, rules)
    return model


if __name__ == "__main__":
    fuzzy_model = build_fuzzy_model()
    input_vars = {'var1': 7, 'var2': 10}

    # Run prediction of Fuzzy Model.
    prediction = fuzzy_model.process_rules(input_vars)
    print("prediction['conclusion1']: ", prediction['conclusion1'])

    # Persist Fuzzy Model.
    with tempfile.TemporaryDirectory() as path:
        os.environ['H1ST_MODEL_REPO_PATH'] = path
        fuzzy_model.persist('my_version_1')

        # Load Fuzzy Model.
        reloaded_fuzzy_model = FuzzyModel().load('my_version_1')

    prediction = reloaded_fuzzy_model.process_rules(input_vars)
    print("prediction['conclusion1']: ", prediction['conclusion1'])
