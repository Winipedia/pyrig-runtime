"""Test module."""

from functools import cache
from pathlib import Path

from pyrig.core.introspection.modules import import_module_from_file

from pyrig_runtime.core.introspection.functions import (
    filter_module_functions,
    module_functions,
)
from pyrig_runtime.core.introspection.inspection import obj_members


def some_function() -> None:
    """Test function."""


@cache
def some_wrapped_function() -> None:
    """Test function."""


def test_module_functions() -> None:
    """Test function."""
    module = import_module_from_file(Path(__file__), __name__)
    funcs = tuple(module_functions(module))
    func_names = {func.__name__ for func in funcs}  # ty:ignore[unresolved-attribute]
    assert some_function.__name__ in func_names
    assert some_wrapped_function.__name__ in func_names
    assert test_module_functions.__name__ in func_names


def test_filter_module_functions() -> None:
    """Test function."""
    module = import_module_from_file(Path(__file__), __name__)
    members = obj_members(module)
    funcs = tuple(filter_module_functions(module, members))
    func_names = {func.__name__ for func in funcs}  # ty:ignore[unresolved-attribute]
    assert some_function.__name__ in func_names
    assert some_wrapped_function.__name__ in func_names
    assert test_module_functions.__name__ in func_names
