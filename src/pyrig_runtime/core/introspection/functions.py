"""Detecting and enumerating function-like objects."""

import inspect
from collections.abc import Callable, Iterator
from types import ModuleType
from typing import Any

from pyrig_runtime.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrap_obj,
)


def module_functions(
    module: ModuleType,
) -> Iterator[Callable[..., Any]]:
    """Yield all functions defined directly in a module.

    Excludes objects imported from other modules.

    Args:
        module: Module to inspect.

    Yields:
        Each function defined in `module`.
    """
    return (
        func
        for _name, func in obj_members(module)
        if is_funclike(func)
        if obj_module(func) is module
    )


def is_funclike(obj: Any) -> bool:
    """Return `True` if an object is a function or any method-like descriptor.

    Covers all forms that may appear as a method or function in a class or
    module namespace:

    - Plain functions and bound methods
    - `staticmethod` and `classmethod` descriptors
    - `property` descriptors
    - Functions wrapped with `functools.wraps` or similar decorators

    Args:
        obj: Object to test.
    """
    return is_func_or_method(unwrap_obj(obj))


def is_func_or_method(obj: Any) -> bool:
    """Return `True` if an object is a plain function or a bound method.

    Does not detect `staticmethod`, `classmethod`, or `property` descriptors
    when accessed through a class `__dict__`.

    Args:
        obj: Object to test.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)
