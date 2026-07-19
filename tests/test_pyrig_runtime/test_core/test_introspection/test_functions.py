"""Test module."""

import sys
from functools import cache

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
    module = sys.modules[__name__]
    funcs = tuple(module_functions(module))

    assert set(funcs) == {
        some_function,
        some_wrapped_function,
        test_filter_module_functions,
        test_module_functions,
    }


def test_filter_module_functions() -> None:
    """Test function."""
    module = sys.modules[__name__]
    members = obj_members(module)
    funcs = tuple(filter_module_functions(module, members))

    assert set(funcs) == {
        some_function,
        some_wrapped_function,
        test_filter_module_functions,
        test_module_functions,
    }
