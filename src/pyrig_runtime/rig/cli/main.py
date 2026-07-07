"""Console-script entry point for pyrig-runtime-based projects."""

from pyrig_runtime.rig.cli.cli import CLI


def main() -> None:
    """Run the CLI application."""
    CLI.I.run()
