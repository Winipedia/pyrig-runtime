"""Test module."""

import os
from collections.abc import Callable
from functools import wraps
from types import ModuleType

import pytest

from pyrig_runtime.core.introspection.classes import classproperty
from pyrig_runtime.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrap_obj,
)


def test_obj_members() -> None:
    """Test function."""
    members = list(obj_members(test_obj_members))
    assert len(members) > 0


def test_obj_module() -> None:
    """Test function."""

    # Test with a function
    def test_function() -> None:
        pass

    module = obj_module(test_function)
    assert module.__name__ == __name__, (
        f"Expected module name {__name__}, got {module.__name__}"
    )

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            pass

        @property
        def test_property(self) -> str:
            return "test"

    method_module = obj_module(TestClass.test_method)
    assert method_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {method_module.__name__}"
    )

    # Test with a property
    prop_module = obj_module(TestClass.test_property)
    assert prop_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {prop_module.__name__}"
    )

    # Test with built-in function
    os_module = obj_module(os.path.join)
    assert "posixpath" in os_module.__name__ or "ntpath" in os_module.__name__, (
        f"Expected posixpath or ntpath module, got {os_module.__name__}"
    )

    # take an obj without a module and check if raises LookupError
    with pytest.raises(LookupError):
        obj_module("string without module")

    with pytest.raises(LookupError):
        # classproperty has fget in slots so it will unwrap to a
        # C member object that has no module, so should raise LookupError
        # we do not want this case handled to keep logic simpler
        # it should be skipped in module_classes with the default
        obj_module(classproperty)

    module = obj_module(classproperty, default=ModuleType("default_module"))
    assert module.__name__ == "default_module"


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
