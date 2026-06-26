"""CLI commands shared across all pyrig-runtime-based projects.

Commands in this module are available in every pyrig-runtime-based project and
reflect the context of the project that invoked them.
"""


def version() -> None:
    """Print the installed version of the invoking project.

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
