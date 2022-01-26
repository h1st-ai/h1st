H1st Graph
==========

H1st Graph is an execution flow chart that allows the incorporation of ML as well as human expert models.

This is an example of a very simple graph which prints hello for each even number x in the input stream, using a conditional RuleBasedModel which is a h1.Model node and a HelloPrinter which is a h1.Action node.


.. code-block:: python

  import h1st as h1

  class RuleBasedModel(h1.Model):
      """
      Simple rule-based model that "predicts" if a given value is an even number
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


The H1st graph itself is created by add()ing nodes incrementally.

Note that the first branch is a h1.Decision which redirects the data flow into the later yes and no nodes based on the RuleBasedModel’s predictions`.

In terms of data flow, the RuleBasedModel node produces a dict of which is then used by h1.Decision to redirect the data stream by looking at the result_field=predictions dict key.

H1st graph by default operates in batch mode, meaning that h1.Decision looks at {"predictions": [{"prediciton": True, ...}, {"prediction": False, }]} and redirect True/False decision points to the to the right yes/no branch as a list.


.. code-block:: python

  g.start()
  g.add(h1.Decision(RuleBasedModel(), result_field="predictions"))
  g.add(yes=HelloPrinter(), no=h1.NoOp())
  g.end()

  results = g.predict({"values": range(6)})


.. code-block::

  Hello world 0!
  Hello world 2!
  Hello world 4!