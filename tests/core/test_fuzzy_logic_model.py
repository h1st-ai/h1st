import math
from unittest import TestCase, skip

import numpy as np
import pandas as pd


import h1st as h1
from fuzzy_logic_model import FuzzyLogicModel

class MyFuzzyLogicModel(FuzzyLogicModel):
    def add_variables(self):
        """
        Add fuzzy variables with membership functions
        """
        self.add_variable(
            range_=np.arange(0, 10, 0.5), 
            name='sensor1', 
            mem_funcs=[('normal', 'gaussian', [3, 3.3]),
                       ('abnormal', 'triangle', [8, 15, 15])], 
            var_type='antecedent'
        )
        self.add_variable(
            range_=np.arange(0, 10, 0.5), 
            name='sensor2', 
            mem_funcs=[('normal', 'gaussian', [3, 3.3]),
                       ('abnormal', 'triangle', [8, 15, 15])], 
            var_type='antecedent'
        )        
        self.add_variable(
            range_=np.arange(0, 10, 0.5), 
            name='problem1', 
            mem_funcs=[('no', 'trapezoid', [0, 0, 4, 6]),
                       ('yes', 'trapezoid', [4, 6, 10, 10])], 
            var_type='consequent'
        )

    def add_rules(self):
        """
        Add fuzzy rules here. Place antecedent type variables in 'if' statement 
        and place consequent type varibles in 'then' statement.
        """
        vars = self.variables
        self.add_rule(
            'rule1', 
            if_=vars['sensor1']['abnormal'] & vars['sensor2']['abnormal'], 
            then_=vars['problem1']['yes'])
        self.add_rule(
            'rule2', 
            if_=vars['sensor1']['normal'], 
            then_=vars['problem1']['no'])
        self.add_rule(
            'rule2', 
            if_=vars['sensor2']['normal'], 
            then_=vars['problem1']['no'])   


class FuzzyLogicModelTestCase(TestCase):
    def test_fuzzy_logic_model(self):
        my_fuzzy_logic_model = MyFuzzyLogicModel()
        sensor_input = {
            'sensor1': 7,
            'sensor2': 10
        }
        prediction = my_fuzzy_logic_model.predict(sensor_input)
        print(prediction)
        assert prediction['problem1'] < 5

        sensor_input = {
            'sensor1': 3,
            'sensor2': 15
        }
        prediction = my_fuzzy_logic_model.predict(sensor_input)
        print(prediction)
        assert prediction['problem1'] < 5        

        sensor_input = {
            'sensor1': 10,
            'sensor2': 5
        }
        prediction = my_fuzzy_logic_model.predict(sensor_input)
        print(prediction)
        assert prediction['problem1'] < 5

        sensor_input = {
            'sensor1': 10,
            'sensor2': 15
        }
        prediction = my_fuzzy_logic_model.predict(sensor_input)
        print(prediction)
        assert prediction['problem1'] > 5        