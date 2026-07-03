"""Detecting and enumerating function-like objects."""

import inspect
from collections.abc import Callable, Iterator
from types import ModuleType
from typing import Any

from pyrig_runtime.core.introspection.inspection import (
    obj_members,
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
    for _name, function in obj_members(module):
        func = unwrap_obj(function)
        if inspect.isfunction(func) and inspect.getmodule(func) is module:
            yield func
