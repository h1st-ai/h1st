class BaseValidator:
    """
    Base class for validator
    """
    def is_applicable(self, schema):
        raise NotImplementedError()

    def validate_type(self, upstream, downstream):
        raise NotImplementedError()
