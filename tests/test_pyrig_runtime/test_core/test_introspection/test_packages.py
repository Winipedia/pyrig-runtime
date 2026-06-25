"""Test module."""

from types import ModuleType

from pyrig.rig.configs.base.config_file import ConfigFile
from pytest_mock import MockerFixture

import pyrig_runtime
from pyrig_runtime import core
from pyrig_runtime.core.dependencies import graph
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.introspection import packages
from pyrig_runtime.core.introspection.packages import (
    discover_subclasses_across_package,
    register_package_modules,
    walk_package,
)
from pyrig_runtime.rig.cli.cli import cli
from pyrig_runtime.rig.cli.cli.cli import CLI


def test_discover_subclasses_across_package() -> None:
    """Test function."""
    subclasses = tuple(
        discover_subclasses_across_package(
            cls=DependencySubclass, package=pyrig_runtime
        )
    )
    assert ConfigFile not in subclasses
    assert CLI in subclasses

    assert all(issubclass(subcls, DependencySubclass) for subcls in subclasses)


def test_register_package_modules(mocker: MockerFixture) -> None:
    """Test function."""
    package = ModuleType(test_register_package_modules.__name__)
    mock_walk_package = mocker.patch(
        walk_package.__module__ + "." + walk_package.__name__,
        return_value=iter([]),
    )
    register_package_modules(package)
    mock_walk_package.assert_called_once_with(package)
    register_package_modules(package)
    # should only call walk_package once due to caching
    mock_walk_package.assert_called_once_with(package)


def test_walk_package() -> None:
    """Test function."""
    modules = list(walk_package(core))

    module_types = {m for m, _ in modules}

    assert pyrig_runtime not in module_types
    assert core not in module_types
    assert cli not in module_types

    assert packages in module_types
    assert graph in module_types
