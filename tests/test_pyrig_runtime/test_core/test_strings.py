"""Tests module."""

import re

import pytest

from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.strings import (
    fully_qualified_name,
    kebab_to_snake_case,
    regex_find,
    snake_to_kebab_case,
)
from pyrig_runtime.rig.cli import shared_subcommands


def test_kebab_to_snake_case() -> None:
    """Test function."""
    project_name = "test-project"
    package_name = kebab_to_snake_case(project_name)
    expected_package_name = "test_project"
    assert package_name == expected_package_name


def test_snake_to_kebab_case() -> None:
    """Test function."""
    package_name = "test_project"
    project_name = snake_to_kebab_case(package_name)
    expected_project_name = "test-project"
    assert project_name == expected_project_name


def test_fully_qualified_name() -> None:
    """Test function."""
    assert (
        fully_qualified_name(shared_subcommands.version)
        == "pyrig_runtime.rig.cli.shared_subcommands.version"
    )

    assert (
        fully_qualified_name(DependencySubclass)
        == "pyrig_runtime.core.dependencies.subclass.DependencySubclass"
    )

    assert fully_qualified_name(DependencySubclass.discovery_module) == (
        "pyrig_runtime.core.dependencies.subclass.DependencySubclass.discovery_module"
    )


def test_regex_find() -> None:
    """Test function."""
    pattern = re.compile(r"^Name:[ \t]*(.*)$", re.MULTILINE)

    text = "Metadata-Version: 2.1\nName: some-package\nVersion: 1.0\n"
    assert regex_find(pattern, text) == "some-package"

    # only the first match is returned, even when the pattern matches more than once
    multi_match_text = "Name: first\nOther: value\nName: second\n"
    assert regex_find(pattern, multi_match_text) == "first"

    with pytest.raises(LookupError):
        regex_find(pattern, "no matching field here")
