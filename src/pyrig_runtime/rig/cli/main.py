"""Console-script entry point for pyrig and pyrig-based projects."""

from pyrig_runtime.rig.cli.cli.cli import CLI


def main() -> None:
    """Run the CLI application."""
    CLI.I.run()
