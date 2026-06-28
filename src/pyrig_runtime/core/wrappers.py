"""Wrapper utilities."""

from collections.abc import Callable
from typing import Any

from pyrig_runtime.core.constants import MISSING


def safe_call[T](
    func: Callable[..., T],
    *args: Any,
    default: T = MISSING,  # ty:ignore[invalid-parameter-default]
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    **kwargs: Any,
) -> T:
    """Call `func`, returning `default` on failure or re-raising if none is given.

    Args:
        func: Callable to invoke.
        *args: Positional arguments forwarded to `func`.
        default: Value to return when a caught exception is raised. If not
            provided, any caught exception propagates unchanged.
        exceptions: Exception types to catch. Defaults to `(Exception,)`.
        **kwargs: Keyword arguments forwarded to `func`.

    Returns:
        The return value of `func(*args, **kwargs)`, or `default` if an
        exception is caught and `default` was provided.
    """
    try:
        return func(*args, **kwargs)
    except exceptions:
        if default is MISSING:
            raise
        return default
