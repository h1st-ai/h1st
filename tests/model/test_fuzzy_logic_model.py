import numpy as np
import os
import tempfile

from h1st.model.fuzzy import (
    FuzzyModeler,
    FuzzyModel,
    FuzzyRules,
    FuzzyVariables,
    FuzzyMembership as fm,
)


def build_fuzzy_logic_model():
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
        'rule1',
        if_term=vars.get('var1')['abnormal'] & vars.get('var2')['abnormal'],
        then_term=vars.get('conclusion1')['yes'],
    )
    rules.add(
        'rule2',
        if_term=vars.get('var1')['normal'],
        then_term=vars.get('conclusion1')['no'],
    )
    rules.add(
        'rule3',
        if_term=vars.get('var2')['normal'],
        then_term=vars.get('conclusion1')['no'],
    )

    modeler = FuzzyModeler()
    model = modeler.build_model(vars, rules)
    return model


class TestFuzzyLogicModelTestCase:
    def test_fuzzy_logic_model(self):
        m = build_fuzzy_logic_model()
        sensor_input = {'var1': 7, 'var2': 10}
        prediction = m.process_rules(sensor_input)
        assert prediction['conclusion1'] < 5

        sensor_input = {'var1': 3, 'var2': 15}
        prediction = m.process_rules(sensor_input)
        assert prediction['conclusion1'] < 5

        sensor_input = {'var1': 10, 'var2': 5}
        prediction = m.process_rules(sensor_input)
        assert prediction['conclusion1'] < 5

        sensor_input = {'var1': 10, 'var2': 15}
        prediction = m.process_rules(sensor_input)
        assert prediction['conclusion1'] > 5

    def test_fuzzy_model_persist_and_load(self):
        m = build_fuzzy_logic_model()
        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path
            m.persist('test_model')

            m = None
            m = FuzzyModel().load('test_model')
            assert m.rules is not None
            sensor_input = {'var1': 10, 'var2': 15}
            prediction = m.process_rules(sensor_input)
            assert prediction['conclusion1'] > 5
