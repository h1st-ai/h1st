from typing import Any

from h1st.core.node import Node


class FilterByKey(Node):
    def __init__(self, key_field: str):
        self.key_name = key_field

    def execute(self, previous_output: Any = None) -> list:
        if isinstance(previous_output, list):
            return list(map(lambda elem: elem[self.key_name], previous_output))
        elif isinstance(previous_output, dict):
            return previous_output[self.key_name]
