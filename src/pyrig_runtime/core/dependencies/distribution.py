"""Utilities for parsing and extracting information from installed distributions."""

import re
from importlib.metadata import Distribution

from pyrig_runtime.core.strings import kebab_to_snake_case, regex_find

REQUIRES_DIST_NAME_PATTERN = re.compile(r"^([a-zA-Z0-9_.-]*)")


def distribution_header_value_pattern(field_name: str) -> re.Pattern[str]:
    """Compile a regex matching every value of a single-line RFC 822 header."""
    return re.compile(rf"^{field_name}:[ \t]*(.*)$", re.MULTILINE)


DISTRIBUTION_NAME_PATTERN = distribution_header_value_pattern("Name")
DISTRIBUTION_REQUIRES_DIST_PATTERN = distribution_header_value_pattern(
    "Requires-Dist",
)
DISTRIBUTION_SUMMARY_PATTERN = distribution_header_value_pattern("Summary")


def distribution_requirement_as_module_name(req: str) -> str:
    """Extract the importable module name from a dependency requirement string.

    Version specifiers, extras notation, and any other non-name characters are
    stripped. Hyphens in the package name are normalized to underscores.

    Args:
        req: A dependency requirement string (
            e.g., `"requests>=2.0,<3.0"` or
            `"my-package[extra]==1.0.0"`or
            `"some.package==1.0.0"`
            ).

    Returns:
        The package name in snake_case (
            e.g., `"requests"`, `"my_package"`, `"some.package"`
        ).
    """
    return kebab_to_snake_case(regex_find(REQUIRES_DIST_NAME_PATTERN, req))


def distribution_summary(metadata: str) -> str:
    """Return the summary recorded in an installed distribution's metadata.

    This function assumes that the package is installed and its
    metadata has a "Summary" field.

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The distribution's summary description.
    """
    return regex_find(DISTRIBUTION_SUMMARY_PATTERN, metadata)


def distribution_name(metadata: str) -> str:
    """Return the name of a distribution from its metadata.

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The name of the distribution.
    """
    return regex_find(DISTRIBUTION_NAME_PATTERN, metadata)


def distribution_requirements(metadata: str) -> list[str]:
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
    end = metadata.find("\n\n")
    return metadata[:end] if end != -1 else metadata


def distribution_metadata(dist: Distribution) -> str | None:
    """Return the full metadata of a distribution."""
    return dist.read_text("METADATA")
