"""Dict with Default Value."""


from typing import Any, Callable


__all__ = ('DefaultDict',)


class DefaultDict(dict):
    """Dict with Default Value."""

    def __init__(self, default: Any, *args: Any, **kwargs: Any):
        """Init Default Dict."""
        super().__init__(*args, **kwargs)

        self.default_factory: Callable[..., Any] = (default
                                                    if callable(default)
                                                    else (lambda: default))

    def __getitem__(self, item: str, /) -> Any:
        """Get item."""
        return (super().__getitem__(item)
                if item in self
                else self.default_factory())

    @property
    def default(self) -> Any:
        """Get default value."""
        return self.default_factory()

    @default.setter
    def default(self, default: Any, /):
        """Set default value."""
        if callable(default):
            self.default_factory: Callable[..., Any] = default

        elif default != self.default_factory():
            self.default_factory: Callable[..., Any] = lambda: default
