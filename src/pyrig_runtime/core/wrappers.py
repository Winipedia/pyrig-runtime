"""Wrapper utilities."""

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
    """Call `func`, returning `default` on failure or re-raising if none is given.

    Args:
        func: Callable to invoke.
        args: Positional arguments forwarded to `func`.
        default: Value to return when a caught exception is raised. If not
            provided, any caught exception propagates unchanged.
        exceptions: Exception types to catch. Defaults to `(Exception,)`.
        kwargs: Keyword arguments forwarded to `func`.

    Returns:
        The return value of `func(*args, **kwargs)`, or `default` if an
        exception is caught and `default` was provided.
    """
    try:
        return func(*args, **(kwargs or {}))
    except exceptions:
        if default is MISSING:
            raise
        return default
