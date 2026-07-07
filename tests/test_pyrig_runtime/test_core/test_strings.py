"""Tests module."""

import re

from pyrig.rig.configs.pyproject import PyprojectConfigFile

from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.strings import (
    dependency_requirement_as_module_name,
    dependency_requirement_split_pattern,
    distribution_summary,
    fully_qualified_name,
    kebab_to_snake_case,
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


def test_dependency_requirement_split_pattern() -> None:
    """Test function."""
    result = dependency_requirement_split_pattern()
    assert isinstance(result, re.Pattern)


def test_dependency_requirement_as_module_name() -> None:
    """Test function."""
    req = "some-package>=1.0.0"
    name = dependency_requirement_as_module_name(req)
    assert name == "some_package"

    req = "another-package==2.0.0"
    name = dependency_requirement_as_module_name(req)
    assert name == "another_package"

    req = "package-without-version"
    name = dependency_requirement_as_module_name(req)
    assert name == "package_without_version"

    req = "complex-package-name[extra1,extra2]>=0.1.0"
    name = dependency_requirement_as_module_name(req)
    assert name == "complex_package_name"

    req = "simplepackage"
    name = dependency_requirement_as_module_name(req)
    assert name == "simplepackage"

    req = "another_package"
    name = dependency_requirement_as_module_name(req)
    assert name == "another_package"


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


def test_distribution_summary() -> None:
    """Test function."""
    assert (
        distribution_summary("pyrig-runtime")
        == PyprojectConfigFile().project_description()
    )
