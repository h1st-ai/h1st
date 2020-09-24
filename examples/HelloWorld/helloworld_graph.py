"""
This is an example of a very simple graph which prints hello for each even number x in the input stream,
using a conditional RuleBasedModel node and a HelloPrinter h1.Action.
"""

import h1st as h1

class RuleBasedModel(h1.Model):
    """
    Simple rule-based model that "predicts" if a given value is an even number.
    """
    def predict(self, input_data: dict) -> dict:
        predictions = [{'prediction': x % 2 == 0, 'value': x} for x in input_data["values"]]
        return {"predictions": predictions}

class HelloPrinter(h1.Action):
    """Print hello to the inputs value"""
    def call(self, command, inputs):
        # Note that H1st does the conditional/filtering orchestration already.
        # All we need to do here is just to print.
        for d in inputs["predictions"]:
            print("Hello world {}!".format(d["value"]))

class NoOp(h1.Action):
    """Do nothing"""
    def call(self, command, inputs):
        pass

def create_graph():
    """Create a graph which prints hello for each even number x in the input stream,
    using a conditional RuleBasedModel node and a HelloPrinter h1.Action."""
    graph = h1.Graph()
    graph.start()\
        .add(h1.Decision(RuleBasedModel(), result_field="predictions"))\
        .add(yes=HelloPrinter(), no=NoOp())
    graph.end()
    return graph

if __name__ == "__main__":
    graph = create_graph()
    results = graph.predict({"values": range(6)})
    # Should get:
    # Hello world 0!
    # Hello world 2!
    # Hello world 4!
