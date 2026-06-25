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
    deps_depending_on_dep,
    discover_equivalent_modules_across_dependents,
    discover_subclasses_across_dependencies,
)
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.rig.cli.cli.cli import CLI


def test_discover_equivalent_modules_across_dependents(mocker: MockerFixture) -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig
    modules = tuple(discover_equivalent_modules_across_dependents(core))
    assert core not in modules
    assert pyrig_core in modules

    # mock deps_depending_on_dep to return a fake dependent package
    # the following is mostly to get 100% test coverage
    mock_all_deps = mocker.patch(
        deps_depending_on_dep.__module__ + "." + deps_depending_on_dep.__name__,
        return_value=[pyrig_runtime],
    )
    modules = tuple(discover_equivalent_modules_across_dependents(core))
    assert core in modules
    mock_all_deps.assert_called_once()

    mock_all_deps.return_value = [typer]
    modules = tuple(discover_equivalent_modules_across_dependents(rig))
    assert not modules


def test_discover_subclasses_across_dependencies() -> None:
    """Test func."""
    subclasses = set(discover_subclasses_across_dependencies(DependencySubclass, rig))
    assert CLI in subclasses
    assert ConfigFile in subclasses
    assert Tool in subclasses
    assert PyprojectConfigFile in subclasses
    assert MirrorTestConfigFile in subclasses


def test_deps_depending_on_dep() -> None:
    """Test function."""
    packages = [*deps_depending_on_dep(pyrig_runtime), pyrig_runtime]
    assert pyrig_runtime in packages
    assert pyrig in packages
