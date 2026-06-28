"""Test module."""

from pyrig_runtime.rig.cli import subcommands


def test_docstring() -> None:
    """Test function."""
    assert (
        subcommands.__doc__
        == """Project-specific CLI commands.

Functions defined directly in this module are registered as top-level CLI
commands. Module-level `typer.Typer` instances are registered as command
groups, with each group's name derived from the kebab-case form of the
variable name.
"""
    )
