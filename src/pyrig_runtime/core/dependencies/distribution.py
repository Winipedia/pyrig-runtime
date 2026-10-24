"""Utilities for parsing metadata text from installed Python distributions."""

import re
from importlib.metadata import Distribution

from pyrig_runtime.core.strings import kebab_to_snake_case, regex_find

REQUIRES_DIST_NAME_PATTERN = re.compile(r"^([a-zA-Z0-9_.-]*)")


DISTRIBUTION_NAME_PATTERN = re.compile(
    r"^Name:[ \t]*(.*)$",
    re.MULTILINE,
)
DISTRIBUTION_REQUIRES_DIST_PATTERN = re.compile(
    r"^Requires-Dist:[ \t]*(.*)$",
    re.MULTILINE,
)
DISTRIBUTION_SUMMARY_PATTERN = re.compile(
    r"^Summary:[ \t]*(.*)$",
    re.MULTILINE,
)


def distribution_header(metadata: str) -> str:
    """Return the header portion of a distribution's metadata.

    The header is the metadata content before the first blank line,
    containing the single-line RFC 822 header fields (e.g. `Name`,
    `Requires-Dist`). If no blank line is found, the entire metadata
    text is returned.

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


def distribution_name(metadata: str) -> str:
    """Return the name of a distribution from its metadata.

    Args:
        metadata: The full metadata of an installed distribution.

    Returns:
        The name of the distribution.
    """
    return regex_find(DISTRIBUTION_NAME_PATTERN, metadata)


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


def distribution_requirements(metadata: str) -> list[str]:
    """Return the list of dependency requirements from a distribution's metadata."""
    return DISTRIBUTION_REQUIRES_DIST_PATTERN.findall(metadata)


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
