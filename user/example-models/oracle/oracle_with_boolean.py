import numpy as np

from h1st.model.fuzzy import (
    FuzzyModeler,
    FuzzyRules,
    FuzzyVariables,
    FuzzyMembership as fm,
)
from h1st.model.oracle import OracleModeler


def build_fuzzy_model():
    fuzzy_vars = FuzzyVariables()
    fuzzy_vars.add(
        var_name='var1',
        var_type='antecedent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('normal', fm.GAUSSIAN, [3, 3.3]),
            ('abnormal', fm.TRIANGLE, [8, 15, 15]),
        ],
    )
    fuzzy_vars.add(
        var_name='var2',
        var_type='antecedent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('normal', fm.GAUSSIAN, [3, 3.3]),
            ('abnormal', fm.TRIANGLE, [8, 15, 15]),
        ],
    )
    fuzzy_vars.add(
        var_name='conclusion1',
        var_type='consequent',
        var_range=np.arange(0, 10, 0.5),
        membership_funcs=[
            ('no', fm.TRAPEZOID, [0, 0, 4, 6]),
            ('yes', fm.TRAPEZOID, [4, 6, 10, 10]),
        ],
    )

    fuzzy_rules = FuzzyRules()
    fuzzy_rules.add(
        'rule1',
        if_term=fuzzy_vars.get('var1')['abnormal'] & fuzzy_vars.get('var2')['abnormal'],
        then_term=fuzzy_vars.get('conclusion1')['yes'],
    )
    fuzzy_rules.add(
        'rule2',
        if_term=fuzzy_vars.get('var1')['normal'],
        then_term=fuzzy_vars.get('conclusion1')['no'],
    )
    fuzzy_rules.add(
        'rule3',
        if_term=fuzzy_vars.get('var2')['normal'],
        then_term=fuzzy_vars.get('conclusion1')['no'],
    )

    modeler = FuzzyModeler()
    model = modeler.build_model(fuzzy_vars, fuzzy_rules)
    return model


def load_data():
    return {}


if __name__ == "__main__":
    fuzzy_teacher = build_fuzzy_model()
    data = load_data()

    modeler = OracleModeler()
    model = modeler.build_model(data=data, teacher=fuzzy_teacher)

    # Run prediction of Oracle Model.
    input_vars = {'var1': 7, 'var2': 10}
    prediction = model.predict(input_vars)
    print("prediction['conclusion1']: ", prediction['conclusion1'])
