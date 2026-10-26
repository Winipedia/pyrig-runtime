"""Test module."""

import inspect
import sys
from collections.abc import Callable
from functools import cached_property, wraps

from pyrig_runtime.core.introspection.inspection import (
    obj_members,
    unwrap_obj,
)


def cls_decorator(cls: type["DecoratedClass"]) -> type["DecoratedClass"]:
    """A simple class decorator that adds an attribute to the class."""

    class DecoratedClassWrapper(cls):  # ty: ignore[unsupported-base]
        some_cls_attr = "decorated"

    return DecoratedClassWrapper


def test_obj_members() -> None:
    """Test function."""
    members = list(obj_members(test_obj_members))
    assert len(members) > 0


def test_unwrap_decorated_cls() -> None:
    """Test function."""
    module = sys.modules[__name__]
    obj = inspect.getattr_static(module, "DecoratedClass")
    assert obj.__name__ == "DecoratedClassWrapper"
    assert obj.some_cls_attr == "decorated"

    unwrapped_obj = unwrap_obj(obj)
    # unwrapping classes does not really work
    assert unwrapped_obj is obj


def test_unwrap_obj() -> None:
    """Test function."""
    unwrapped_func = unwrap_obj(_deeply_decorated_func)
    assert unwrapped_func.__name__ == "_deeply_decorated_func", (
        f"Expected '_deeply_decorated_func', got {unwrapped_func.__name__}"
    )

    unwrapped_method = unwrap_obj(
        _TestDeeplyNestedClassMethod.deeply_nested_cls_method,
    )
    assert unwrapped_method.__name__ == "deeply_nested_cls_method", (
        f"Expected 'deeply_nested_cls_method', got {unwrapped_method.__name__}"
    )

    uncalled = inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_property")
    unwrapped_property = unwrap_obj(uncalled)
    assert unwrapped_property.__name__ == "some_property"

    unwrapped_static_method = unwrap_obj(
        inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_static_method"),
    )
    assert unwrapped_static_method.__name__ == "some_static_method"

    unwrapped_cls_method = unwrap_obj(
        inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_cls_method"),
    )
    assert unwrapped_cls_method.__name__ == "some_cls_method"


def _dec_a[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def _dec_b[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def _dec_c[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@_dec_a
@_dec_b
@_dec_c
def _deeply_decorated_func() -> str:
    return "deep"


@cls_decorator
class DecoratedClass:
    """A class that has been decorated with a class decorator."""

    some_cls_attr = "class_value"


class _TestDeeplyNestedClassMethod:
    @classmethod
    @_dec_a
    @_dec_b
    @_dec_c
    def deeply_nested_cls_method(cls) -> str:
        return "deeply_nested"

    @property
    def some_property(self) -> str:
        return "property_value"

    @staticmethod
    def some_static_method() -> str:
        return "static_value"

    @classmethod
    def some_cls_method(cls) -> str:
        return "class_value"

    @cached_property
    def some_cached_property(self) -> str:
        return "cached_value"
