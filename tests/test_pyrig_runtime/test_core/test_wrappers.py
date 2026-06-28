"""Test module."""

import pytest

from pyrig_runtime.core.wrappers import safe_call


def test_safe_call() -> None:
    """Test function."""
    assert safe_call(int, "1") == 1

    with pytest.raises(
        ValueError, match=r"invalid literal for int\(\) with base 10: 'not-an-int'"
    ):
        safe_call(int, "not-an-int")

    assert safe_call(int, "not-an-int", default=-1) == -1
