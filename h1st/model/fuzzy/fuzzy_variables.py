import logging
from typing import Any

import skfuzzy
from skfuzzy import control as skctrl

from h1st.model.fuzzy.enums import FuzzyMembership as fm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuzzyVariables:
    def __init__(self) -> None:
        self.variables = {}

    def _setup_triangle_func(self, var, values):
        if len(values) != 3:
            raise ValueError(
                (
                    f"TRIANGLE membership function needs 3 "
                    f"values. Provided {len(values)} values."
                )
            )
        return skfuzzy.trimf(var, values)

    def _setup_trapezoid_func(self, var, values):
        if len(values) != 4:
            raise ValueError(
                (
                    f"TRAPEZOID membership function needs 4 "
                    f"values. Provided {len(values)} values."
                )
            )
        return skfuzzy.trapmf(var, values)

    def _setup_gaussian_func(self, var, values):
        if len(values) != 2:
            raise ValueError(
                (
                    f"GAUSSIAN membership function needs 2 "
                    f"values. Provided {len(values)} values."
                )
            )
        return skfuzzy.gaussmf(var, values[0], values[1])

    def _setup_sigmoid_func(self, var, values):
        if len(values) != 2:
            raise ValueError(
                (
                    f"SIGMOID membership function needs 2 "
                    f"values. Provided {len(values)} values."
                )
            )
        return skfuzzy.sigmf(var, values[0], values[1])

    def _setup_rsigmoid_func(self, var, values):
        if len(values) != 2:
            raise ValueError(
                (
                    f"SIGMOID membership function needs 2 "
                    f"values. Provided {len(values)} values."
                )
            )
        return -1 * (skfuzzy.sigmf(var, values[0], values[1]) - 1)

    FUNCTION_DICT = {
        fm.TRIANGLE: _setup_triangle_func,
        fm.TRAPEZOID: _setup_trapezoid_func,
        fm.GAUSSIAN: _setup_gaussian_func,
        fm.SIGMOID: _setup_sigmoid_func,
        fm.RSIGMOID: _setup_rsigmoid_func
    }

    def add(
        self, var_name: str, var_type: str, var_range: list, membership_funcs: list
    ) -> None:
        """
        Add a fuzzy variable with their type and membership functions.

        :param var_name: the name of variable
        :param var_type: the varilable type should be either consequent or antecedent
        :param var_range: the range of variable
        :param membership_funcs: this is the list of tuple(membership_func_name, membership_func_type, membership_func_range)
            there are four different kinds of membership_func_type that are supported and their membership_func_range should follow the following formats.
            GAUSSIAN: [mean, sigma]
            SIGMOID: [offset, width]
            TRIANGLE: [a, b, c] where a <= b <= c
            TRAPEZOID: [a, b, c, d] where a <= b <= c <= d

        .. code-block:: python
            :caption: example
            vars = FuzzyVariables()
            vars.add(
                var_name='var1',
                var_type='antecedent',
                var_range=np.arange(0, 15+1e-5, 0.5),
                membership_funcs=[('normal', fm.GAUSSIAN, [3, 3.3]),
                                  ('abnormal', fm.TRIANGLE, [8, 15, 15])]
            )
        """
        # Check variable type.
        if var_type == "antecedent":
            fuzzy_var = skctrl.Antecedent(var_range, var_name)
        elif var_type == "consequent":
            fuzzy_var = skctrl.Consequent(var_range, var_name)
        else:
            logger.error(f"{var_type} is not supported type")
            raise ValueError(f"{var_type} is not supported type")

        # Add membership function and its values.
        for mem_func_name, mem_func_type, mem_func_vals in membership_funcs:
            if mem_func_type in self.FUNCTION_DICT.keys():
                fuzzy_var[mem_func_name] = self.FUNCTION_DICT[mem_func_type](
                    self, fuzzy_var.universe, mem_func_vals
                )
            else:
                raise ValueError(f"{mem_func_type} is not supported.")

        self.variables[var_name] = fuzzy_var

    def remove(self, var_name: str) -> None:
        if var_name in self.variables:
            self.variables.pop(var_name)
        else:
            raise KeyError(f"variable name {var_name} does not exist.")

    def get(self, var_name: str) -> Any:
        if var_name in self.variables:
            return self.variables[var_name]
        else:
            raise KeyError(f"variable name {var_name} does not exist.")

    def visualize(self) -> None:
        print("=== Antecedents & Consequents ===")
        for v in self.variables.values():
            if isinstance(v, skctrl.Antecedent):
                v.view()
        for v in self.variables.values():
            if isinstance(v, skctrl.Consequent):
                v.view()
