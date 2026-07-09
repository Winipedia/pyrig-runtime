"""Constants used throughout the project."""

import re

MISSING = object()

NON_DEPENDENCY_CHAR_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]")
