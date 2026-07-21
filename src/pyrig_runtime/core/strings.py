"""String conversion utilities for Python package naming conventions."""

import re
from types import FunctionType, MethodType


def fully_qualified_name(obj: MethodType | FunctionType | type) -> str:
    """Return the fully qualified name of a callable.

    The returned name consists of the callable's module and qualified name,
    preserving any enclosing classes or functions.
    E.g., for a method `foo` in class `Bar` in module `baz`, the fully qualified
    name is `"baz.Bar.foo"`.

    Args:
        obj: The callable (function, method, or class).

    Returns:
        The callable's fully qualified name.
    """
    return f"{obj.__module__}.{obj.__qualname__}"


def kebab_to_snake_case(value: str) -> str:
    """Convert a kebab-case string to snake_case, replacing hyphens with underscores."""
    return value.replace("-", "_")


def snake_to_kebab_case(value: str) -> str:
    """Convert a snake_case string to kebab-case, replacing underscores with hyphens."""
    return value.replace("_", "-")


def regex_find(pattern: re.Pattern[str], text: str) -> str:
    """Return the first captured group from a regex search on the given text.

    Args:
        pattern: A compiled regex pattern with at least one capturing group.
        text: The text to search within.

    Returns:
        The first captured group from the regex search.

    Raises:
        LookupError: If no match is found for the pattern in the text.
    """
    match = pattern.search(text)
    if match is None:
        msg = f"No match found for pattern {pattern.pattern} in text."
        raise LookupError(msg)
    return match[1]
