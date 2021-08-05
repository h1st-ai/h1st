"""
This is an example of a very simple rule-based (if-then-else) H1st model.
It doesn't need any data or training, and hence has only a predict() function.
"""

from h1st.model.rule_based_model import RuleBasedModel


class SimpleRuleBasedModel(RuleBasedModel):
    """
    Simple rule-based model that "predicts" if a given value is an even number
    """

    def predict(self, input_data: dict) -> dict:
        predictions = [{'prediction': x % 2 == 0, 'value': x} for x in input_data["values"]]
        return {"predictions": predictions}


if __name__ == "__main__":
    m = SimpleRuleBasedModel()
    xs = list(range(6))
    results = m.predict({"values": xs})
    predictions = results["predictions"]
    print(f"RuleBasedModel's predictions for {xs} are {predictions}")
