"""Version display command for pyrig-runtime-based project CLIs."""

from importlib.metadata import version

import typer

from pyrig_runtime.rig.cli.cli.cli import CLI


def project_version() -> None:
    """Print the installed version of the invoking project.

    Prints the version of whichever project's CLI entry point was used to
    invoke this command, not pyrig-runtime's own version. The project must be
    installed (an editable install is sufficient) for its version to be available.
    """
    project_name = CLI.I.project_name()
    typer.echo(f"{project_name} {version(project_name)}")
