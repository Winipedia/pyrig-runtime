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
    """Return the module where a method-like object is defined.

    Unwraps the object first, so decorated functions, properties, classmethods,
    and staticmethods all resolve to their defining module. Useful for
    distinguishing objects defined in a module from those merely imported into
    it.

    Args:
        obj: Method-like object (function, method, property, staticmethod,
            classmethod, or decorated callable).
        default: Module to return when the origin cannot be determined. When
            `None` and the module cannot be determined, `LookupError` is raised.

    Returns:
        The module where `obj` is defined.

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
    """Unwrap a method-like object to its underlying function.

    Strips every layer until no more can be removed: the bound-method,
    classmethod, and staticmethod descriptors (`__func__`), the property getter
    (`fget`), and `functools.wraps`-style decorator chains. For a property, the
    getter function is returned.

    Args:
        obj: Callable that may be wrapped (bound method, property,
            staticmethod, classmethod, or any decorated function).

    Returns:
        The underlying unwrapped function object.
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
