from enum import Enum

class Explainable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Explainable`, i.e., they can self-describe their properties and behaviors, as well as
    self-explain certain decisions they have made. For example, an `Explainable` `Model` should be
    able to report the data that was used to train it, provide an importance-ranked list of its
    input features on a global basis, and provide a detailed explanation of a specific decision it made
    at some specified time or on a given set of inputs in the past.
    """

    class Constituency(Enum):
        """
        A Constituency is the party that is asking for an explanation. This is important to recognize,
        because the same question from different constituencies may warrant different responses: a Data Scientist
        may wish to get a response about detailed model metrics, whereas a Consumer may wish to get a response
        in plain English why her credit application was denied.
        """
        DATA_SCIENTIST = 10
        BUSINESS_MANAGER = 20
        CUSTOMER = 30
        USER = 40
        CONSUMER = 50
        REGULATOR = 60
        LEGISLATOR = 70
        ANY = 99
        OTHER = 100
    
    @property
    def description(self):
        return getattr(self, "__description", {})
    
    @description.setter
    def description(self, value):
        setattr(self, "__description", value)
    
    def describe(self, constituency=Constituency.ANY):
        return {}

    def explain(self, constituency=Constituency.ANY, decision=None):
        return {}

    def performance(self, constituency=Constituency.ANY):
        return {}

    def consequence(self, constituency=Constituency.ANY, decision=None):
        return {}

    def document(self, constituency=Constituency.ANY):
        return {}

