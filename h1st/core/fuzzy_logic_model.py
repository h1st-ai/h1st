import skfuzzy as fuzz
from skfuzzy import control as ctrl

from h1st.core.rule_based_model import RuleBasedModel

class FuzzyLogicModel(RuleBasedModel):
    def __init__(self):
        self.classes = []
        self.rules = {}
        self.variables = {}
        self.mem_funcs = {
            'triangle': fuzz.trimf,
            'trapezoid': fuzz.trapmf,
            'gaussian': fuzz.gaussmf,
        }
        self.add_variables()
        self.add_rules()
        self.build()

    def add_variables(self):
        """
        Add fuzzy variables with membership functions

        Example: 
        self.add_variable(
            range_=np.arange(0, 10, 0.5), 
            name='sensor1', 
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
        """        
        pass

    def add_rules(self):
        """
        Add fuzzy rules here. Place antecedent type variables in 'if' statement 
        and place consequent type varibles in 'then' statement.

        Example:
        self.add_rule(
            'rule1', 
            if_=self.variables['sensor1']['abnormal'], 
            then_=self.variables['problem1']['yes'])
        self.add_rule(
            'rule2', 
            if_=self.variables['sensor1']['normal'], 
            then_=self.variables['problem1']['no'])            
        """   
        pass

    def build(self):
        ctrl_system = ctrl.ControlSystem(list(self.rules.values()))
        self.css = ctrl.ControlSystemSimulation(ctrl_system)

    def add_rule(self, name, if_, then_):
        rule = ctrl.Rule(if_, then_)
        self.rules[name] = rule

    def remove_rule(self, name):
        del self.rules[name]

    def add_variable(self, range_, name, mem_funcs, var_type):
        if var_type == 'antecedent':
            variable = ctrl.Antecedent(range_, name)
        elif var_type == 'consequent':
            variable = ctrl.Consequent(range_, name)
            if name not in self.classes:
                self.classes.append(name)
        else:
            print(f'{var_type} is not supported type')
            return None
        for mem_name, mem_func_type, mem_range in mem_funcs:
            if mem_func_type != 'gaussian':
                variable[mem_name] = self.mem_funcs[mem_func_type](
                    variable.universe, mem_range)
            else:
                variable[mem_name] = self.mem_funcs[mem_func_type](
                    variable.universe, mem_range[0], mem_range[1])
            
        self.variables[name] = variable

    def remove_variable(self, name):
        del self.variables[name]    

    def visualize_variable(self, name):
        if name in self.variables:
            self.variables[name].view()
        else:
            print(f"{name} not found")

    def get_fuzzy_output(self, input_data: dict):
        for key, value in input_data.items():
            self.css.input[key] = value
        self.css.compute()
        classification = {}
        for cls in self.classes:
            classification[cls] = round(self.css.output[cls], 5)
        return classification
