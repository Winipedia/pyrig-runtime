"""Test module."""

from pyrig_runtime.core.constants import (
    MISSING,
)


def test_missing() -> None:
    """Test function."""
    assert MISSING is not None
    assert isinstance(MISSING, object)
    assert MISSING is not MISSING.__class__()
    assert MISSING is not object()
