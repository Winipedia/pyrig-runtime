"""module."""

import inspect
from types import ModuleType

import pytest
from pyrig.rig import configs
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.configs.community.license import LicenseConfigFile
from pyrig.rig.configs.docs.builder import DocsBuilderConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig_pypi.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile as PyPIDeployWorkflowConfigFile,
)

from pyrig_runtime import rig
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.rig.cli.cli import CLI


class A(DependencySubclass):
    """Test class."""

    @classmethod
    def discovery_module(cls) -> ModuleType:
        """Return the discovery module."""
        return rig

    @classmethod
    def merge_key(cls) -> str:
        """Return the merge key."""
        return "merge_key"


class B(A):
    """Test class."""

    __module__ = rig.__name__


class C(B):
    """Test class."""

    __module__ = rig.__name__


class D(A):
    """Test class."""

    __module__ = rig.__name__


class E(A):
    """Test class."""

    __module__ = rig.__name__


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

        leaf = A.leaf()
        assert issubclass(leaf, A)
        assert issubclass(leaf, B)
        assert issubclass(leaf, C)
        assert issubclass(leaf, D)
        assert issubclass(leaf, E)

        assert leaf not in (A, B, C, D, E)

    def test_concrete_leaves(self) -> None:
        """Test method."""
        result = tuple(ConfigFile.concrete_leaves())
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)
        assert all(not inspect.isabstract(subclass) for subclass in result)

    def test_leaves(self) -> None:
        """Test method."""
        leaves = tuple(A.leaves())
        assert len(leaves) == 1
        leaf = leaves[0]
        assert issubclass(leaf, A)
        assert issubclass(leaf, B)
        assert issubclass(leaf, C)
        assert issubclass(leaf, D)
        assert issubclass(leaf, E)
        assert leaf not in (A, B, C, D, E)

    def test_sorted_subclasses(self) -> None:
        """Test method."""
        subclasses = (
            DocsBuilderConfigFile,
            ReadmeConfigFile,
            PyprojectConfigFile,
            LicenseConfigFile,
        )
        result = ConfigFile.sorted_subclasses(subclasses)
        assert result == [
            ReadmeConfigFile,
            LicenseConfigFile,
            PyprojectConfigFile,
            DocsBuilderConfigFile,
        ]

    def test_subclasses(self) -> None:
        """Test method."""
        subclasses = tuple(ConfigFile.subclasses())
        assert len(subclasses) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in subclasses)

        assert TOMLConfigFile in subclasses

        assert DeployWorkflowConfigFile in subclasses
        assert DeployWorkflowConfigFile.L in subclasses

        assert PyPIDeployWorkflowConfigFile in subclasses
        assert PyPIDeployWorkflowConfigFile.L in subclasses

    def test_merge_key(self) -> None:
        """Test method."""
        assert CLI.merge_key() == CLI.__name__


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
