Rule-Based Model
================

Rule-based model is an example of usingour human knowledge to solve a problem. You could also use boolean logic, fuzzy logic, or make decision based on statistcs or myriad other ways that humans do to solve problems.

Rule-based model is very useful to solve the cold start problem, where data is not available.

In H1st framework, a human rule model can be implemented by subclassing the h1.Model class and implementing only the predict() function. Basically, it’s a just a model with no training (though training is not forbidden and is sometimes is useful for human models too).

This particular simple model “predicts” if each given value in a stream is an even number or not.

.. code-block:: python

  import h1st as h1

  class RuleBasedModel(h1.Model):
      """
      Simple rule-based model that "predicts" if a given value is an even number
      """
      def predict(self, input_data: dict) -> dict:
          predictions = [{'prediction': x % 2 == 0, 'value': x} for x in input_data["values"]]
          return {"predictions": predictions}

  m = RuleBasedModel()
  xs = list(range(6))
  results = m.predict({"values": xs})
  predictions = results["predictions"]
  print(f"RuleBasedModel's predictions for {xs} are {predictions}")


.. code-block::

  RuleBasedModel's predictions for [0, 1, 2, 3, 4, 5] are [{'prediction': True, 'value': 0}, {'prediction': False, 'value': 1}, {'prediction': True, 'value': 2}, {'prediction': False, 'value': 3}, {'prediction': True, 'value': 4}, {'prediction': False, 'value': 5}]
