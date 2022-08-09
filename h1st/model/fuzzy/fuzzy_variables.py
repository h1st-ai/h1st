import logging
from typing import NoReturn

import skfuzzy
from skfuzzy import control as skctrl
from skfuzzy.control.term import Term

from h1st.model.fuzzy.enums import FuzzyMembership as fm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyVariables:

    def add(self, var_name: str, var_type: str, var_range: list, membership_funcs: list): #  -> NoReturn
        """
        Add a variable with their type and membership functions.

        :param range_: the range of variable
        :param name: the name of variable
        :param membership_funcs: this is the list of tuple(membership_func_name, membership_func_type, membership_func_range)
            There are three different kinds of membership_func_type that are supported and their membership_func_range should follow the following formats.
            gaussian: [mean, sigma]
            triangle: [a, b, c] where a <= b <= c
            trapezoid: [a, b, c, d] where a <= b <= c <= d
        :param type_: the varilable type should be either consequent or antecedent

        .. code-block:: python
            :caption: example
            fv = FuzzyVariables()
            fv.add(
                var_name='service_quality',
                var_type='antecedent',
                var_range=np.arange(0, 10, 0.5),
                membership_funcs=[('Bad', 'gaussian', [2, 1]),
                                  ('Decent', 'triangle', [3, 5, 7]),
                                  ('Great', 'trapezoid', [6, 8, 10, 10])]
            )
        """
        # Check variable type. 
        if var_type == 'antecedent':
            fuzzy_var = skctrl.Antecedent(var_range, var_name)
        elif var_type == 'consequent':
            fuzzy_var = skctrl.Consequent(var_range, var_name)
        else:
            logger.error(f'{var_type} is not supported type')
            raise ValueError(f'{var_type} is not supported type')

        # Add membership function and its values.
        for mem_func_name, mem_func_type, mem_func_vals in membership_funcs:
            if mem_func_type == fm.TRIANGLE:
                if len(mem_func_vals) != 3:
                    raise ValueError((f'TRIANGLE membership function needs 3 '
                        'values. Provided {len(mem_func_vals)} values.'))
                fuzzy_var[mem_func_name] = skfuzzy.trimf(
                    fuzzy_var.universe, mem_func_vals)
            elif mem_func_type == fm.TRAPEZOID:
                if len(mem_func_vals) != 4:
                    raise ValueError((f'TRAPEZOID membership function needs 4 '
                        'values. Provided {len(mem_func_vals)} values.'))
                fuzzy_var[mem_func_name] = skfuzzy.trapmf(
                    fuzzy_var.universe, mem_func_vals)
            elif mem_func_type == fm.GAUSSIAN:
                if len(mem_func_vals) != 2:
                    raise ValueError((f'GAUSSIAN membership function needs 2 '
                        'values. Provided {len(mem_func_vals)} values.'))
                fuzzy_var[mem_func_name] = skfuzzy.gaussmf(
                    fuzzy_var.universe, mem_func_vals[0], mem_func_vals[1])
            else:
                raise ValueError(f'{mem_func_type} is not supported.')

        setattr(self, var_name, fuzzy_var)
        # self.vars[name] = variable

    def remove(self, var_name: str) -> NoReturn:
        if hasattr(self, var_name):
            delattr(self, var_name)

    def visualize(self) -> None:
        print("=== Antecedents & Consequents ===")
        for var in self.__dict__.values():
            if isinstance(var, skfuzzy.control.Antecedent):
                var.view()

        for var in self.__dict__.values():
            if isinstance(var, skfuzzy.control.Consequent):
                var.view()

