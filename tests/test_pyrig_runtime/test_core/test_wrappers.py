"""Test module."""

import pytest

from pyrig_runtime.core.wrappers import safe_call


def test_safe_call() -> None:
    """Test function."""
    assert safe_call(int, args=("1",)) == 1

    with pytest.raises(
        ValueError,
        match=r"invalid literal for int\(\) with base 10: 'not-an-int'",
    ):
        safe_call(int, args=("not-an-int",))

    assert safe_call(int, args=("not-an-int",), default=-1) == -1

    def some_func(x: int, y: int) -> int:
        return x + y

    assert safe_call(some_func, args=(1, 2)) == 3  # noqa: PLR2004
    assert safe_call(some_func, kwargs={"x": 2, "y": 2}) == 4  # noqa: PLR2004
    assert safe_call(some_func, args=(1,), kwargs={"y": 3}) == 4  # noqa: PLR2004
