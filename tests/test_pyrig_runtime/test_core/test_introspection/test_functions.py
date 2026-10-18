"""Test module."""

import sys
from functools import cache

from pyrig_runtime.core.introspection.functions import (
    filter_module_funcs,
    module_funcs,
)
from pyrig_runtime.core.introspection.inspection import obj_members


def some_func() -> None:
    """Test function."""


@cache
def some_wrapped_func() -> None:
    """Test function."""


def test_module_funcs() -> None:
    """Test function."""
    module = sys.modules[__name__]
    funcs = tuple(module_funcs(module))

    assert set(funcs) == {
        some_func,
        some_wrapped_func,
        test_filter_module_funcs,
        test_module_funcs,
    }


def test_filter_module_funcs() -> None:
    """Test function."""
    module = sys.modules[__name__]
    members = obj_members(module)
    funcs = tuple(filter_module_funcs(module, members))

    assert set(funcs) == {
        some_func,
        some_wrapped_func,
        test_filter_module_funcs,
        test_module_funcs,
    }
