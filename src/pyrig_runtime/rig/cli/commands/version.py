"""Version display command for pyrig-runtime-based project CLIs."""

from importlib.metadata import version

import typer

from pyrig_runtime.rig.cli.cli import CLI


def project_version() -> None:
    """Print the name and installed version of the project running this CLI.

    Reports the version of the project whose CLI is currently running.
    The project must be installed for its version to be available.
    """
    project_name = CLI.I.project_name()
    typer.echo(f"{project_name} {version(project_name)}")
