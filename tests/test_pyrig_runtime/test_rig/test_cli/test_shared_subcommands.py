"""module."""

from collections.abc import Callable, Iterable
from types import FunctionType

from pyrig_runtime.rig.cli import shared_subcommands
from pyrig_runtime.rig.cli.commands.version import project_version
from pyrig_runtime.rig.cli.shared_subcommands import version


def test_version(
    command_works: Callable[[FunctionType], bool],
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_works(version)
    assert command_calls_function(version, project_version, [])


def test_docstring() -> None:
    """Test function."""
    assert (
        shared_subcommands.__doc__
        == """Shared CLI commands for all dependent packages.

In every installed pyrig-runtime based package functions defined directly in this
module are registered as top-level CLI commands and module-level `typer.Typer` instances
are registered as command groups, with each group's name derived from the kebab-case
form of the variable name.
"""
    )
