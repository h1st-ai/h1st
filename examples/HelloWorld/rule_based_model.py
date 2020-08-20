"""
This is an example of a very simple rule-based (if-then-else) H1st model.
It doesn't need any data or training, and hence has only a predict() function.
Run this example as: % python3 rule_based_model.py
"""

import h1st as h1

class RuleBasedModel(h1.Model):
    def predict(sef, input_data):
        value = input_data["value"]
        is_odd = (value % 2 == 0)
        return is_odd


def hello_world():
    m = RuleBasedModel()
    for value in range(6):
        print("Prediction for " + str(value) + " is " + str(m.predict({"value": value})))

hello_world()