"""(Python) Path-related utilities."""


from pathlib import Path
import sys


__all__ = ('add_cwd_to_py_path',)


def add_cwd_to_py_path():
    """Add current working directory to Python path."""
    if (cwd_path_str := str(Path.cwd().resolve(strict=True))) not in sys.path:
        sys.path.append(cwd_path_str)
