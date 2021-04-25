from enum import Enum

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
    An Aspect is the type of the question being asked. Different types of questions may warrant very different responses.
    For example, `how do you prevent an autocyber attack in the future?` is an `Operational` type question
    asking you to describe how the system will be used in the event of a future attack.
    Or `what if your model is wrong? - this is a type of `Accountability` question.
    """
    ACCOUNTABLE = 10
    FUNCTIONAL = 20
    OPERATIONAL = 30
    ANY = 99
    OTHER = 100
