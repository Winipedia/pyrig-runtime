"""Test module."""

from types import ModuleType

from pytest_mock import MockerFixture

import pyrig_runtime
from pyrig_runtime import core
from pyrig_runtime.core.dependencies import graph
from pyrig_runtime.core.introspection import packages
from pyrig_runtime.core.introspection.packages import (
    is_package,
    register_package_modules,
    walk_package,
)
from pyrig_runtime.rig.cli import cli


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


def test_is_package() -> None:
    """Test function."""
    assert is_package(pyrig_runtime)
    assert is_package(core)
    assert not is_package(cli)
    assert not is_package(packages)
