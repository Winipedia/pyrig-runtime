"""Test module."""

import pyrig
import typer
from pyrig import core as pyrig_core
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool
from pytest_mock import MockerFixture

import pyrig_runtime
from pyrig_runtime import core, rig
from pyrig_runtime.core.dependencies.discovery import (
    dependency_graph,
    discover_dependent_packages,
    discover_equivalent_modules_across_dependencies,
    discover_subclasses_across_dependencies,
)
from pyrig_runtime.core.dependencies.graph import DependencyGraph
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.rig.cli.cli import CLI


def test_discover_equivalent_modules_across_dependencies(mocker: MockerFixture) -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig
    modules = tuple(discover_equivalent_modules_across_dependencies(core))
    assert core not in modules
    assert pyrig_core in modules

    # mock discover_dependent_packages to return a fake dependent package
    # the following is mostly to get 100% test coverage
    mock_all_deps = mocker.patch(
        discover_dependent_packages.__module__
        + "."
        + discover_dependent_packages.__name__,
        return_value=[pyrig_runtime],
    )
    modules = tuple(discover_equivalent_modules_across_dependencies(core))
    assert core in modules
    mock_all_deps.assert_called_once()

    mock_all_deps.return_value = [typer]
    modules = tuple(discover_equivalent_modules_across_dependencies(rig))
    assert not modules


def test_discover_subclasses_across_dependencies() -> None:
    """Test func."""
    subclasses = set(discover_subclasses_across_dependencies(DependencySubclass, rig))
    assert CLI in subclasses
    assert ConfigFile in subclasses
    assert Tool in subclasses
    assert PyprojectConfigFile in subclasses
    assert MirrorTestConfigFile in subclasses

    class AlsoADependencySubclass(DependencySubclass):
        pass

    AlsoADependencySubclass.__module__ = "not_a_real_dependency.rig"
    subclasses = set(discover_subclasses_across_dependencies(DependencySubclass, rig))
    assert AlsoADependencySubclass in subclasses


def test_discover_dependent_packages() -> None:
    """Test function."""
    packages = [*discover_dependent_packages(pyrig_runtime), pyrig_runtime]
    assert pyrig_runtime in packages
    assert pyrig in packages


def test_dependency_graph() -> None:
    """Test function."""
    assert isinstance(dependency_graph(), DependencyGraph)
    assert dependency_graph() is dependency_graph()
    assert dependency_graph() is not DependencyGraph()
    assert "typer" not in dependency_graph().nodes
    assert pyrig.__name__ in dependency_graph().nodes
