"""Shared CLI commands for all dependent packages.

In every installed pyrig-runtime based package functions defined directly in this
module are registered as top-level CLI commands and module-level `typer.Typer` instances
are registered as command groups, with each group's name derived from the kebab-case
form of the variable name.
"""


def version() -> None:
    """Print the installed version.

    Reports the version of whichever project's CLI entry point was used to
    invoke this command, not pyrig-runtime's own version. The project must be
    installed; an editable install is sufficient.

    Example:
        ```
        $ uv run myproject version
        myproject 0.4.1
        ```
    """
    from pyrig_runtime.rig.cli.commands.version import project_version  # noqa: PLC0415

    project_version()
