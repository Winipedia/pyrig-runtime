"""Test module."""

import inspect
from collections.abc import Callable
from functools import wraps

from pyrig_runtime.core.introspection.classes import classproperty
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

    @classproperty
    def class_property(cls) -> str:  # noqa: N805
        return "class_property"


def test_unwrap_obj() -> None:
    """Test function."""
    unwrapped_func = unwrap_obj(_deeply_decorated_func)
    assert unwrapped_func.__name__ == "_deeply_decorated_func", (
        f"Expected '_deeply_decorated_func', got {unwrapped_func.__name__}"
    )

    unwrapped_method = unwrap_obj(
        _TestDeeplyNestedClassMethod.deeply_nested_class_method
    )
    assert unwrapped_method.__name__ == "deeply_nested_class_method", (
        f"Expected 'deeply_nested_class_method', got {unwrapped_method.__name__}"
    )

    uncalled_property = inspect.getattr_static(
        _TestDeeplyNestedClassMethod, "class_property"
    )
    unwrapped_property = unwrap_obj(uncalled_property)
    assert unwrapped_property.__name__ == "class_property"
    assert unwrapped_property(_TestDeeplyNestedClassMethod) == "class_property"
