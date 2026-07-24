"""Utilities for invoking callables with exception handling."""

from collections.abc import Callable
from typing import Any, overload

from pyrig_runtime.core.constants import MISSING


@overload
def safe_call[T, D](
    func: Callable[..., T],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    default: D,
    exceptions: tuple[type[BaseException], ...] = ...,
) -> T | D: ...
@overload
def safe_call[T](
    func: Callable[..., T],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    exceptions: tuple[type[BaseException], ...] = ...,
) -> T: ...
def safe_call(
    func: Callable[..., Any],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    default: Any = MISSING,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Any:
    """Call `func`, returning `default` if a caught exception is raised.

    Args:
        func: Callable to invoke.
        args: Positional arguments forwarded to `func`.
        kwargs: Keyword arguments forwarded to `func`.
        default: Value to return when a caught exception is raised. If
            omitted, the exception propagates instead.
        exceptions: Exception types to catch. Defaults to `(Exception,)`.

    Returns:
        The return value of `func(*args, **kwargs)`, or `default` if a
        caught exception is raised and `default` was provided.
    """
    try:
        return func(*args, **(kwargs or {}))
    except exceptions:
        if default is MISSING:
            raise
        return default
