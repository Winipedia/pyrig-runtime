"""String conversion utilities for Python package naming conventions."""

import re


def kebab_to_snake_case(value: str) -> str:
    """Convert a kebab-case string to snake_case, replacing hyphens with underscores."""
    return value.replace("-", "_")


def snake_to_kebab_case(value: str) -> str:
    """Convert a snake_case string to kebab-case, replacing underscores with hyphens."""
    return value.replace("_", "-")


def dependency_requirement_as_package_name(dep_req: str) -> str:
    """Extract the bare package name from a dependency requirement string.

    Version specifiers, extras notation, and any other non-name characters are
    stripped. Hyphens in the package name are normalized to underscores.

    Args:
        dep_req: A dependency requirement string (e.g., `"requests>=2.0,<3.0"` or
            `"my-package[extra]==1.0.0"`).

    Returns:
        The package name in snake_case (e.g., `"requests"` or `"my_package"`).
    """
    return kebab_to_snake_case(
        dependency_requirement_split_pattern().split(dep_req, maxsplit=1)[0]
    )


def dependency_requirement_split_pattern() -> re.Pattern[str]:
    """Return a compiled regex pattern matching characters outside a package name.

    The pattern matches any character that is not alphanumeric, an underscore,
    a hyphen, or a period.
    """
    # re.compile is already internally cached by Python
    return re.compile(r"[^a-zA-Z0-9_.-]")
