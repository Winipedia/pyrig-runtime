"""Test module."""

import inspect
import sys
from collections.abc import Callable
from functools import cached_property, wraps
from typing import Any

from pyrig_runtime.core.introspection.inspection import (
    obj_members,
    unwrap_obj,
)


def test_obj_members() -> None:
    """Test function."""
    members = list(obj_members(test_obj_members))
    assert len(members) > 0


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


class _TestDeeplyNestedClassMethod:
    @classmethod
    @_dec_a
    @_dec_b
    @_dec_c
    def deeply_nested_class_method(cls) -> str:
        return "deeply_nested"

    @property
    def some_property(self) -> str:
        return "property_value"

    @staticmethod
    def some_static_method() -> str:
        return "static_value"

    @classmethod
    def some_class_method(cls) -> str:
        return "class_value"

    @cached_property
    def some_cached_property(self) -> str:
        return "cached_value"


def class_decorator(cls: type["DecoratedClass"]) -> type["DecoratedClass"]:
    """A simple class decorator that adds an attribute to the class."""

    class DecoratedClassWrapper(cls):
        some_class_attr = "decorated"

    return DecoratedClassWrapper


@class_decorator
class DecoratedClass:
    """A class that has been decorated with a class decorator."""

    some_class_attr = "class_value"


def test_unwrap_decorated_class() -> None:
    """Test function."""
    module = sys.modules[__name__]
    obj = inspect.getattr_static(module, "DecoratedClass")
    assert obj.__name__ == "DecoratedClassWrapper"
    assert obj.some_class_attr == "decorated"

    unwrapped_obj = unwrap_obj(obj)
    # unwrapping classes does not really work
    assert unwrapped_obj is obj


class ClassDecorator:
    """A class decorator that decorates a function."""

    def __init__(self, func: Callable[..., str]) -> None:
        """Initialize the decorator with the function to decorate."""
        self.fget = func
        self.fget.some_func_attr = "decorated"  # ty:ignore[unresolved-attribute]

    def __call__(self, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        """Call the decorated function."""
        return self.fget(*args, **kwargs)


@ClassDecorator
def class_decorated_function() -> str:
    """A function that has been decorated with a class decorator."""
    return "decorated_function"


def test_unwrap_class_decorated_function() -> None:
    """Test function."""
    module = sys.modules[__name__]
    obj = inspect.getattr_static(module, "class_decorated_function")
    assert isinstance(obj, ClassDecorator)
    assert obj.__class__.__name__ == "ClassDecorator"
    assert getattr(obj.fget, "some_func_attr", None) == "decorated"

    assert obj() == "decorated_function"
    unwrapped_obj = unwrap_obj(obj)
    assert unwrapped_obj.__name__ == "class_decorated_function"
    assert unwrapped_obj() == "decorated_function"


def test_unwrap_obj() -> None:
    """Test function."""
    unwrapped_func = unwrap_obj(_deeply_decorated_func)
    assert unwrapped_func.__name__ == "_deeply_decorated_func", (
        f"Expected '_deeply_decorated_func', got {unwrapped_func.__name__}"
    )

    unwrapped_method = unwrap_obj(
        _TestDeeplyNestedClassMethod.deeply_nested_class_method,
    )
    assert unwrapped_method.__name__ == "deeply_nested_class_method", (
        f"Expected 'deeply_nested_class_method', got {unwrapped_method.__name__}"
    )

    uncalled = inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_property")
    unwrapped_property = unwrap_obj(uncalled)
    assert unwrapped_property.__name__ == "some_property"

    unwrapped_static_method = unwrap_obj(
        inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_static_method"),
    )
    assert unwrapped_static_method.__name__ == "some_static_method"

    unwrapped_class_method = unwrap_obj(
        inspect.getattr_static(_TestDeeplyNestedClassMethod, "some_class_method"),
    )
    assert unwrapped_class_method.__name__ == "some_class_method"
