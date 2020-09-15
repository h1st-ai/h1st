from .explainable import Explainable
from .describable import Describable
from .auditable import Auditable
from .debiasable import Debiasable

class Trustable(Auditable, Debiasable, Describable, Explainable):
    """
    Base class for all `Trustable` interfaces
    """