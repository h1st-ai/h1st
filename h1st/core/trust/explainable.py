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

    class Aspect(Enum):
        """
        An Aspect is the type of question being asked. Different types of questions may warrant very different responses. 
        For example, `how do you prevent an autocyber attack in the future?` is an `Operational` 
        type question asking you to describe how the system handle a future attack. 
        Or `what if your model is wrong? - this is a type of `Accountability` question.
        """
        ACCOUNTABLE = 10
        FUNCTIONAL = 20
        OPERATIONAL = 30
        ANY = 99
        OTHER = 100

    @property
    def description(self):
        return getattr(self, "__description", {})
    
    @description.setter
    def description(self, value):
        setattr(self, "__description", value)

    def describe(self, constituency=Constituency.ANY, apect=Aspect.ANY):
        '''
        Returns a description of the model's behavior and properties based on `Who's asking` for `what`.

            Parameters:
                constituent : str
                    The Constituency asking for the explanation `Who`
                    DATA_SCIENTIST
                    BUSINESS_MANAGER
                    CUSTOMER
                    USER
                    CONSUMER
                    REGULATOR
                    LEGISLATOR
                    ANY
                    OTHER

                aspect : str
                    The Aspect of the question `what`
                    ACCOUNTABLE
                    FUNCTIONAL
                    OPERATIONAL
                    ANY
                    OTHER

            Returns:
                out : Description of Model's behavior and properties (SHAP)               
        '''
        return {}

    def explain(self, constituency=Constituency.ANY, apect=Aspect.ANY,decision=None):
        '''
        Returns an explanation for a decision made by the Model based on `Who's asking` and `why`.

            Parameters:
                constituent : str or int
                    The Constituency asking for the explanation
                    DATA_SCIENTIST or 10
                    BUSINESS_MANAGER or 20
                    CUSTOMER or 30
                    USER or 40
                    CONSUMER or 50
                    REGULATOR or 60
                    LEGISLATOR or 70
                    ANY or 99
                    OTHER or 100

                aspect : str or int
                    The Aspect of the question (Accountable, Functional, Operational)
                    ACCOUNTABLE or 10
                    FUNCTIONAL or 10
                    OPERATIONAL or 30
                    ANY or 99
                    OTHER or 100

                decision : array-like: the input data of the decision to be explained

            Returns:
                out : Specific decision explanation (SHAP or LIME)               
        '''
        return {}
