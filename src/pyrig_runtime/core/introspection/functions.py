"""Utilities for Python functions."""

import inspect
from collections.abc import Callable, Iterable, Iterator
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
    yield from filter_module_functions(module, obj_members(module))


def filter_module_functions(
    module: ModuleType,
    members: Iterable[Any],
) -> Iterator[Callable[..., Any]]:
    """Yield functions from `members` defined directly in `module`.

    Args:
        module: Module to filter functions for.
        members: Iterable of candidate members to filter.

    Yields:
        Each function defined in `module` from `members`.
    """
    for member in members:
        unwrapped_member = unwrap_obj(member)
        if (
            inspect.isfunction(unwrapped_member)
            and unwrapped_member.__module__ == module.__name__
        ):
            yield member
