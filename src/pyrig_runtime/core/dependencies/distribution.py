"""Utilities for parsing metadata text from installed Python distributions."""

import re
from importlib.metadata import Distribution

from pyrig_runtime.core.strings import kebab_to_snake_case, regex_find

REQUIRES_DIST_NAME_PATTERN = re.compile(r"^([a-zA-Z0-9_.-]*)")


def distribution_header_value_pattern(field_name: str) -> re.Pattern[str]:
    """Compile a regex that matches a single-line metadata header field.

    Matches lines of the form `field_name: value`. Use `findall` on the
    result to collect every value when the header repeats.

    Args:
        field_name: Name of the header field to match, exactly as it
            appears in the metadata (e.g. `Name`).

    Returns:
        A case-sensitive pattern with each match's value captured in the
        first group.
    """
    return re.compile(rf"^{field_name}:[ \t]*(.*)$", re.MULTILINE)


DISTRIBUTION_NAME_PATTERN = distribution_header_value_pattern("Name")
DISTRIBUTION_REQUIRES_DIST_PATTERN = distribution_header_value_pattern(
    "Requires-Dist",
)
DISTRIBUTION_SUMMARY_PATTERN = distribution_header_value_pattern("Summary")


def distribution_requirement_as_module_name(req: str) -> str:
    """Extract the importable module name from a dependency requirement string.

    Version specifiers, extras, and anything else after the package name
    are discarded. Hyphens are normalized to underscores; dots are kept, so
    namespace packages remain dotted.

    Args:
        req: A dependency requirement string, e.g. `my-package[extra]>=1.0`.

    Returns:
        The package name in snake_case, e.g. `my_package`.

    Example:
        >>> distribution_requirement_as_module_name("my-package[extra]>=1.0.0")
        'my_package'
    """
    return kebab_to_snake_case(regex_find(REQUIRES_DIST_NAME_PATTERN, req))


def distribution_summary(metadata: str) -> str:
    """Return the summary recorded in an installed distribution's metadata.

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The distribution's summary description.

    Raises:
        LookupError: If the metadata has no `Summary` field.
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

    The header is the metadata content before the first blank line,
    containing the single-line RFC 822 header fields (e.g. `Name`,
    `Requires-Dist`).

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The header portion of the distribution's metadata.
    """
    end = metadata.find("\n\n")
    return metadata[:end] if end != -1 else metadata


def distribution_metadata(dist: Distribution) -> str | None:
    """Return the full metadata text of a distribution, or `None` if it has none."""
    return dist.read_text("METADATA")
