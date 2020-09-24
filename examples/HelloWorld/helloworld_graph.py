"""
This is an example of a very simple rule-based (if-then-else) H1st model.
It doesn't need any data or training, and hence has only a predict() function.
"""

import h1st as h1

from rule_based_model import RuleBasedModel 

class HelloPrinter(h1.Action):
    """Print hello to the inputs value"""
    def call(self, command, inputs):
        for value, prediction in zip(inputs["values"], inputs["predictions"]):
            if prediction:
                print(f"Hello world {value}!")

class NoOp(h1.Action):
    """Do nothing"""
    def call(self, command, inputs):
        pass

def create_graph():
    """Create a graph which prints hello to the input value if RuleBasedModel "classifier" returns true (given the same input value)"""
    graph = h1.Graph()
    graph.start()\
        .add(h1.Decision(RuleBasedModel(), result_field="predictions"))\
        .add(yes=HelloPrinter(), no=NoOp())
    graph.end()
    return graph

if __name__ == "__main__":
    graph = create_graph()
    # should print out:
    # "Hello world 0!"
    # "Hello world 2!"
    # "Hello world 4!"
    graph.predict({"values": range(6)})
