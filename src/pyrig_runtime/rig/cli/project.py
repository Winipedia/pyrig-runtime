"""Helpers for identifying the invoking pyrig-runtime-based project."""

import sys
from pathlib import Path


def project_name_from_argv() -> str:
    """Return the invoking project's console-script name from ``sys.argv[0]``."""
    return Path(sys.argv[0]).stem
