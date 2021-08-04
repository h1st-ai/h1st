"""
This is an example of a very simple graph which prints hello for each even number x in the input stream,
using a conditional RuleBasedModel node and a HelloPrinter h1.Action.
"""

from h1st.h1flow.h1flow import Graph
from h1st.h1flow.h1step import Action, Decision, NoOp
from rule_based_model import SimpleRuleBasedModel


class HelloPrinter(Action):
    """Print hello to the inputs value"""

    def call(self, command, inputs):
        # Note that H1st does the conditional/filtering orchestration already.
        # All we need to do here is just to print.
        for d in inputs["predictions"]:
            print("Hello world {}!".format(d["value"]))


def create_graph():
    """Create a graph which prints hello for each even number x in the input stream,
    using a conditional RuleBasedModel node and a HelloPrinter h1.Action."""
    graph = Graph()
    graph.start() \
        .add(Decision(SimpleRuleBasedModel(), result_field="predictions")) \
        .add(yes=HelloPrinter(), no=NoOp())
    graph.end()
    return graph


if __name__ == "__main__":
    generated_graph = create_graph()
    results = generated_graph.predict({"values": range(6)})
    # Should get:
    # Hello world 0!
    # Hello world 2!
    # Hello world 4!
