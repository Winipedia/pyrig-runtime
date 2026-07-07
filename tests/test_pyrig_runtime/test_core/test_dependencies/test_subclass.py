"""module."""

import inspect

import pytest
from pyrig.rig import configs
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig_pypi.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile as PyPIDeployWorkflowConfigFile,
)

from pyrig_runtime import rig
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.rig.cli.cli import CLI


class TestDependencySubclass:
    """Test class."""

    def test___str__(self) -> None:
        """Test method."""
        assert isinstance(str(CLI.I), str)
        assert str(CLI.I) == str(CLI) == str(CLI.L)

    def test_discovery_module(self) -> None:
        """Test method."""
        assert issubclass(ConfigFile, DependencySubclass)
        assert ConfigFile.discovery_module() == configs
        assert DependencySubclass.discovery_module() is rig

    def test_sort_key(self) -> None:
        """Test method."""
        assert DependencySubclass.sort_key() == DependencySubclass.__name__

    def test_leaf(self) -> None:
        """Test method."""
        leaf = ProgrammingLanguage.leaf()
        assert issubclass(leaf, ProgrammingLanguage)
        assert ProgrammingLanguage.leaf() is ProgrammingLanguage.leaf().leaf()

        with pytest.raises(
            RuntimeError, match=r"Multiple leaf subclasses found for .*."
        ):
            _ = Tool.leaf()

    def test_concrete_subclasses(self) -> None:
        """Test method."""
        result = tuple(ConfigFile.concrete_subclasses())
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)
        assert all(not inspect.isabstract(subclass) for subclass in result)

    def test_subclasses(self) -> None:
        """Test method."""
        subclasses = tuple(ConfigFile.subclasses())
        assert len(subclasses) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in subclasses)

    def test_subclasses_sorted(self) -> None:
        """Test method."""
        subclasses = (
            ReadmeConfigFile,
            PyprojectConfigFile,
            LicenseConfigFile,
        )
        result = ConfigFile.subclasses_sorted(subclasses)
        assert result == [
            LicenseConfigFile,
            PyprojectConfigFile,
            ReadmeConfigFile,
        ]


class TestDependencySubclassMeta:
    """Test class."""

    def test___str__(self) -> None:
        """Test method."""
        assert (
            str(DependencySubclass)
            == DependencySubclass.__module__ + "." + DependencySubclass.__name__
        )

    def test_I(self) -> None:  # noqa: N802
        """Test method."""
        with pytest.raises(TypeError):
            _ = DependencySubclass()

        assert CLI.I is CLI.I
        assert isinstance(CLI.I, CLI)

    def test_L(self) -> None:  # noqa: N802
        """Test method."""
        assert MirrorTestConfigFile.L.L.L is MirrorTestConfigFile.L
        assert DeployWorkflowConfigFile.L is PyPIDeployWorkflowConfigFile
        assert CLI.L is CLI
