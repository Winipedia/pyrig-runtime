"""Utilities for inspecting Python objects."""

import inspect
from collections.abc import Callable, Iterator
from types import ModuleType
from typing import Any


def obj_members(
    obj: Any, predicate: Callable[[Any], bool] | None = None
) -> Iterator[tuple[str, Any]]:
    """Yield the members of an object as name-value pairs without invoking descriptors.

    Members are read statically, so properties with side effects are not
    triggered. `__annotate__` and `__annotate_func__` are always excluded
    from the result.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        predicate: Optional filter. When given, only members for which it
            returns `True` are included.

    Yields:
        `(name, value)` pairs for the matching members of `obj`.
    """
    return (
        (member, value)
        for member, value in inspect.getmembers_static(obj, predicate=predicate)
        if member not in {"__annotate__", "__annotate_func__"}
    )


def obj_module(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module defining the underlying object.

    Resolves through any decorator or descriptor layers, so the returned module
    reflects where the underlying object is defined rather than where any
    outer wrapper may originate.

    Args:
        obj: Python object whose defining module to locate.
        default: Module to return when the defining module cannot be determined.
            When `None` and the module cannot be determined, `LookupError` is
            raised.

    Returns:
        The module where the underlying `obj` is defined.

    Raises:
        LookupError: If the defining module cannot be determined and `default`
            is `None`.
    """
    module = inspect.getmodule(unwrap_obj(obj)) or default
    if module is None:
        msg = f"Could not determine module of {obj}"
        raise LookupError(msg)
    return module


def unwrap_obj(obj: Any) -> Any:
    """Unwrap a Python object to its innermost underlying object.

    Strips property getters, bound-method and descriptor wrappers, and
    `functools.wraps`-style decorator chains until no further unwrapping is
    possible.

    Args:
        obj: Python object that may be wrapped, including bound
            methods, properties, classmethods, staticmethods, and decorated
            functions.

    Returns:
        The innermost Python object after all wrapping layers have been removed.
    """
    prev = None
    while prev is not obj:
        prev = obj
        if func := getattr(obj, "__func__", None):
            obj = func
        if fget := getattr(obj, "fget", None):
            obj = fget
        obj = inspect.unwrap(obj)
    return obj
