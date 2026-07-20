"""String conversion utilities for Python package naming conventions."""

import re
from importlib.metadata import Distribution, metadata
from types import FunctionType, MethodType

NON_DEPENDENCY_CHAR_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]")


def distribution_header_value_pattern(field_name: str) -> re.Pattern[str]:
    """Compile a regex matching every value of a single-line RFC 822 header."""
    return re.compile(rf"^{field_name}:[ \t]*(.*)$", re.MULTILINE)


DISTRIBUTION_NAME_PATTERN = distribution_header_value_pattern("Name")
DISTRIBUTION_REQUIRES_DIST_PATTERN = distribution_header_value_pattern("Requires-Dist")


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
        NON_DEPENDENCY_CHAR_PATTERN.split(dep_req, maxsplit=1)[0],
    )


def distribution_summary(name: str) -> str:
    """Return the summary recorded in an installed distribution's metadata.

    This function assumes that the package is installed and its
    metadata has a "Summary" field.

    Args:
        name: Name of an installed distribution (e.g. `"requests"`).

    Returns:
        The distribution's summary description.
    """
    return metadata(name)["Summary"]


def distribution_name(metadata: str) -> str:
    """Return the name of a distribution from its metadata.

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The name of the distribution.
    """
    return DISTRIBUTION_NAME_PATTERN.findall(metadata)[0]


def distribution_requires(metadata: str) -> list[str]:
    """Return the list of dependency requirements from a distribution's metadata."""
    return DISTRIBUTION_REQUIRES_DIST_PATTERN.findall(metadata)


def distribution_header(metadata: str) -> str:
    """Return the header portion of a distribution's metadata.

    The header is the part of the metadata before the first blank line. It
    contains all single-line RFC 822 headers, including "Name" and
    "Requires-Dist".

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The header portion of the distribution's metadata.
    """
    header_end = metadata.find("\n\n")
    return metadata[:header_end] if header_end != -1 else metadata


def distribution_metadata(dist: Distribution) -> str | None:
    """Return the full metadata of a distribution."""
    return dist.read_text("METADATA")


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
