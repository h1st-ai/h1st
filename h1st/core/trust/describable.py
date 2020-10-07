import weakref
from .shap_model_describer import SHAPModelDescriber
from .enums import Constituency, Aspect
from .describer import Describer
from .auditable import Auditable


class Describable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that are `Describable, i.e., they can self-describe their properties and behaviors. For example,
    a `Describable` `Model` should be able to report the data that was used to train it, provide an
    importance-ranked list of its input features on a global basis, etc.
    """
    _instances = set()

    def __init__(self):
        self._instances.add(weakref.ref(self))

    def __call__(self, function):
        def wrapped_function(*args):
            self.data = args[0]
            for obj in self.getinstances():
                print(self)
                # if self._is_described(obj):
                #     print(function.__name__)
            # print(" Prepped Data ", self)
            # for obj in self.getinstances():
            #     print(obj)
            #     print(type(obj).__name__)
            return function(*args)

        return wrapped_function

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def _is_described(self, obj):
        return str(type(obj).__name__) != 'Describable'

    @property
    def description(self):
        return getattr(self, "__description", {})

    @description.setter
    def description(self, value):
        setattr(self, "__description", value)

    # def get_describabile_information(self):
    #     pass

    def describe(self, constituency=Constituency.ANY, aspect=Aspect.ANY):
        """
        Returns a description of the model's behavior and properties based on `Who's asking` for `what`.

            Parameters:
                constituent : Constituency: The Constituency asking for the explanation `Who`
                aspect : The Aspect of the question. `What`

            Returns:
                out : Description of Model's behavior and properties
        """
        describer = Describer(self)
        describer.shap_describer = SHAPModelDescriber(
            self.get_base_model__prepared_data())
        # describer.generate_report(constituency, aspect)
        return describer
