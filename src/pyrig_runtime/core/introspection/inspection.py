"""Utilities for inspecting Python objects."""

import inspect
from collections.abc import Callable, Iterator
from types import FunctionType
from typing import Any, overload


def obj_members(
    obj: object,
    predicate: Callable[[Any], bool] | None = None,
) -> Iterator[Any]:
    """Yield the values of an object's members without invoking descriptors.

    Members are read statically, so properties with side effects are not
    triggered. `__annotate__` and `__annotate_func__` are always excluded
    from the result.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        predicate: Optional filter. When given, only members for which it
            returns `True` are included.

    Returns:
        The values of the matching members of `obj`.
    """
    return (
        value
        for member, value in inspect.getmembers_static(obj, predicate=predicate)
        if member not in {"__annotate__", "__annotate_func__"}
    )


@overload
def unwrap_obj(obj: Callable[..., Any]) -> FunctionType | type: ...
@overload
def unwrap_obj(obj: property) -> FunctionType: ...
@overload
def unwrap_obj[T](obj: T) -> T: ...
def unwrap_obj(obj: Any) -> Any:
    """Unwrap a Python object to its innermost underlying object.

    Recognizes properties, bound methods, classmethods, staticmethods, and
    `functools.wraps`-style decorator chains. All layers are removed, not just
    the outermost one.

    Args:
        obj: Python object to unwrap.

    Returns:
        The innermost Python object after all wrapping layers have been removed.
    """
    prev = None
    while prev is not obj:
        prev = obj
        if (func := getattr(obj, "__func__", None)) is not None:
            obj = func
        if (fget := getattr(obj, "fget", None)) is not None:
            obj = fget
        if hasattr(obj, "__wrapped__"):
            obj = inspect.unwrap(obj)
    return obj
