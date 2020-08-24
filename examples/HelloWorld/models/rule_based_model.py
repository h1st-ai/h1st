"""
This is an example of a very simple rule-based (if-then-else) H1st model.
It doesn't need any data or training, and hence has only a predict() function.
"""

import h1st as h1

class RuleBasedModel(h1.Model):
    def predict(sef, input_data):
        is_odd = (input_data["value"] % 2 == 0)
        return is_odd