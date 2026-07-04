"""String conversion utilities for Python package naming conventions."""

import re
from importlib.metadata import metadata
from types import FunctionType, MethodType


def kebab_to_snake_case(value: str) -> str:
    """Convert a kebab-case string to snake_case, replacing hyphens with underscores."""
    return value.replace("-", "_")


def snake_to_kebab_case(value: str) -> str:
    """Convert a snake_case string to kebab-case, replacing underscores with hyphens."""
    return value.replace("_", "-")


def dependency_requirement_as_module_name(dep_req: str) -> str:
    """Extract the importable module name from a dependency requirement string.

    Version specifiers, extras notation, and any other non-name characters are
    stripped. Hyphens in the package name are normalized to underscores.

    Args:
        dep_req: A dependency requirement string (
            e.g., `"requests>=2.0,<3.0"` or
            `"my-package[extra]==1.0.0"`or
            `"some.package==1.0.0"`
        ).

    Returns:
        The package name in snake_case (
            e.g., `"requests"`, `"my_package"`, `"some.package"`
        ).
    """
    return kebab_to_snake_case(
        dependency_requirement_split_pattern().split(dep_req, maxsplit=1)[0]
    )


def dependency_requirement_split_pattern() -> re.Pattern[str]:
    """Return a compiled regex pattern matching characters outside a package name.

    Returns:
        A pattern matching any character that is not alphanumeric, an
        underscore, a hyphen, or a period.
    """
    return re.compile(r"[^a-zA-Z0-9_.-]")


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


def distribution_summary(name: str) -> str:
    """Return the summary recorded in an installed distribution's metadata.

    Args:
        name: Name of an installed distribution (e.g. `"requests"`).

    Returns:
        The distribution's summary description.
    """
    return metadata(name)["Summary"]
