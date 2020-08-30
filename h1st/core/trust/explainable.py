class Explainable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Explainable`, i.e., they can self-describe their properties and behaviors, as well as
    self-explain certain decisions they have made. For example, an `Explainable` `Model` should be
    able to report the data that was used to train it, provide an importance-ranked list of its
    input features on a global basis, and provide a detailed explanation of a specific decision it made
    at some specified time or on a given set of inputs in the past.
    """

    def describe(self):
        pass # to be implemented

    def explain(self, decision=None):
        pass # to be implemented