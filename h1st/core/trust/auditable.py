import weakref
from datetime import datetime


class Auditable:
    """
    A *Trustworthy-AI* interface that defines the capabilities of objects (e.g., `Models`, `Graphs`)
    that can self-record and report an audit trail of their activities and input/output artifacts.
    For example, an `Auditable` `Model` should be able to record and even retain its training data set,
    the training data scientist, the timestamp, model metrics, etc. available for query at any time in
    the future.
    """

    _instances = set()

    def __init__(self, is_audit=None):
        self._instances.add(weakref.ref(self))
        self.is_audit = is_audit
        self.audit_trail = {}
        self.audit_trail['model'] = [
            str(type(obj).__name__) for obj in self.getinstances()
            if self._is_audited(obj)
        ]

    def __call__(self, function):
        def wrapped_function(*args):
            function_output = function(*args)
            for obj in self.getinstances():

                if self._is_audited(obj):
                    print(function.__name__)

                # print(self._get_function_audit_trail(
                #     args, function_output))
                # self.audit_trail[str(
                #     function.__name__)] = self._get_function_audit_trail(
                #         args, function_output)

            return function_output

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

    def _get_datetime(self):
        return datetime.now().strftime("%b %d, %Y, %H:%M:%S")

    def _is_audited(self, obj):
        return str(type(obj).__name__) != 'Auditable' and obj.is_audit

    def _get_function_audit_trail(self, args, function_output):
        _tmp_dict = {}
        _tmp_dict['input_args'] = args
        _tmp_dict['output'] = function_output
        _tmp_dict['timestamp'] = self._get_datetime()
        return _tmp_dict


# audit = Auditable()
# @property
# def audit_trailing(self):
#     return getattr(self, "__audit_trailing", False)

# @audit_trailing.setter
# def audit_trailing(self, value):
#     setattr(self, "__audit_trailing", value)

# def audit_trail_get(self, key):
#     pass  # to be implemented

# def audit_trail_set(self, key, value):
#     if not self.audit_trailing: return
#     # to be implemented

# def audit_trail_delete(self, key):
#     pass  # to be implemented
