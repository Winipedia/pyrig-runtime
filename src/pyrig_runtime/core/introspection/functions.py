"""Utilities for Python functions."""

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
    for _name, func in obj_members(module):
        unwrapped_func = unwrap_obj(func)
        if (
            inspect.isfunction(unwrapped_func)
            and inspect.getmodule(unwrapped_func) is module
        ):
            yield func
