class SchemaValidationResult:
    """
    This class is used to capture the validation result. All the validation
    errors are captured in the ``errors`` property::

        result = SchemaValidator().validate(..., ...)
        if not result.success:
            print(result.errors)

    """
    def __init__(self, errors=None):
        self._errors = errors or []

    @property
    def errors(self):
        """
        List of validation errors. This list is empty if there is no error.
        """
        return self._errors

    @property
    def success(self):
        """
        Flag to indicate if there is no validation error
        """
        return len(self._errors) == 0

    def merge(self, other, key=None):
        """
        :meta private:
        """
        # TODO: allow access error by key
        if key:
            for msg in other:
                self._errors.append(
                    f'{key}: {msg}'
                )
        else:
            self._errors += list(other)

    def __iter__(self):
        return iter(self._errors)

    def __eq__(self, other):
        if isinstance(other, SchemaValidationResult):
            return self.errors == other.errors

        if isinstance(other, list):
            return self.errors == other

        raise ValueError(f'Can not compare to {other}')

    def __add__(self, other) -> 'SchemaValidationResult':
        if isinstance(other, SchemaValidationResult):
            return SchemaValidationResult(self.errors + other.errors)

        if isinstance(other, SchemaValidationResult):
            return SchemaValidationResult(self.errors + other)

        raise ValueError(f'Can not add to {other}')

    def __bool__(self):
        return self.success

    def display(self):
        """
        Display the errors to console.
        """
        # pylint: disable=undefined-variable,import-outside-toplevel
        try:
            # in IPython
            from IPython import get_ipython
            from IPython.display import HTML

            if get_ipython():
                msg = self._format_error_html()
                display(HTML("\n".join(msg)))  # display in IPython
            else:
                raise ImportError('dummy')
        except ImportError:
            print("\n".join(self._format_error_plain()))

    def _format_error_html(self):
        if self.success:
            msg = ['<span style="color: green">SUCCESS</span>: no issues are found']
        else:
            msg = ['<span style="color: yellow">WARNING:</span> schema mismatch is detected']

            msg.append("<ul>")
            for err in self.errors:
                msg.append(f"<li>{err}</li>")
            msg.append("</ul>")

        return msg

    def _format_error_plain(self):
        if self.success:
            msg = ["SUCCESS: no issues are found"]
        elif len(self.errors) == 1:
            msg = [f"WARNING: schema mismatch is detected: {self.errors[0]}"]
        else:
            msg = ["WARNING: schema mismatch is detected"]
            for err in self.errors:
                msg.append(f"- {err}")

        return msg

    def _repr_html_(self):
        return "\n".join(self._format_error_html())
