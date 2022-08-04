import numpy as np
import os
import tempfile

from h1st.model.fuzzy import FuzzyLogicModeler, \
    FuzzyLogicModel, FuzzyLogicRules


def build_fuzzy_logic_model():
    flr = FuzzyLogicRules()
    flr.add_variable(
        range_=np.arange(0, 10, 0.5),
        name='sensor1',
        membership_funcs=[('normal', 'gaussian', [3, 3.3]),
                            ('abnormal', 'triangle', [8, 15, 15])],
        type_='antecedent'
    )
    flr.add_variable(
        range_=np.arange(0, 10, 0.5),
        name='sensor2',
        membership_funcs=[('normal', 'gaussian', [3, 3.3]),
                            ('abnormal', 'triangle', [8, 15, 15])],
        type_='antecedent'
    )
    flr.add_variable(
        range_=np.arange(0, 10, 0.5),
        name='problem1',
        membership_funcs=[('no', 'trapezoid', [0, 0, 4, 6]),
                            ('yes', 'trapezoid', [4, 6, 10, 10])],
        type_='consequent'
    )
    flr.add_rule(
        'rule1',
        if_=flr.vars['sensor1']['abnormal'] & flr.vars['sensor2']['abnormal'],
        then_=flr.vars['problem1']['yes'])
    flr.add_rule(
        'rule2',
        if_=flr.vars['sensor1']['normal'],
        then_=flr.vars['problem1']['no'])
    flr.add_rule(
        'rule2',
        if_=flr.vars['sensor2']['normal'],
        then_=flr.vars['problem1']['no'])

    modeler = FuzzyLogicModeler()
    model = modeler.build_model(flr)
    return model


class TestFuzzyLogicModelTestCase():
    def test_fuzzy_logic_model(self):
        fuzzy_logic_model = build_fuzzy_logic_model()
        sensor_input = {
            'sensor1': 7,
            'sensor2': 10
        }
        prediction = fuzzy_logic_model.predict(sensor_input)
        assert prediction['problem1'] < 5

        sensor_input = {
            'sensor1': 3,
            'sensor2': 15
        }
        prediction = fuzzy_logic_model.predict(sensor_input)
        assert prediction['problem1'] < 5

        sensor_input = {
            'sensor1': 10,
            'sensor2': 5
        }
        prediction = fuzzy_logic_model.predict(sensor_input)
        assert prediction['problem1'] < 5

        sensor_input = {
            'sensor1': 10,
            'sensor2': 15
        }
        prediction = fuzzy_logic_model.predict(sensor_input)
        assert prediction['problem1'] > 5

    def test_fuzzy_model_persist_and_load(self):
        fuzzy_logic_model = build_fuzzy_logic_model()
        with tempfile.TemporaryDirectory() as path:
            os.environ['H1ST_MODEL_REPO_PATH'] = path

            fuzzy_logic_model.persist('test_model')
            
            fuzzy_logic_model = None
            fuzzy_logic_model = FuzzyLogicModel().load('test_model')
            assert fuzzy_logic_model.rules is not None
            sensor_input = {
                'sensor1': 10,
                'sensor2': 15
            }
            prediction = fuzzy_logic_model.predict(sensor_input)
            assert prediction['problem1'] > 5
