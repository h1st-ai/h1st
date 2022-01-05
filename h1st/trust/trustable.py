from .explainable import Explainable
from .describable import Describable
from .auditable import Auditable
from .debiasable import Debiasable


# __TODO__: implement AI-RULE interfaces


class Trustable(Auditable, Debiasable, Describable, Explainable):
    """
    Base class for all `Trustable` interfaces
    """
