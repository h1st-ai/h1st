from ..rule_based_model import RuleBasedModel

def test_rule_based_model():
    m = RuleBasedModel()
    for value in range(6):
        print("Prediction for " + str(value) + " is " + str(m.predict({"value": value})))