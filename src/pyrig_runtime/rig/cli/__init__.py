"""Command-line interface layer for pyrig-runtime-based projects.

Assembles and runs the command-line application with commands discovered
across the dependency chain at runtime. Projects that depend on pyrig-runtime
gain a CLI entry point automatically and can extend it with project-specific
commands without explicit registration.
"""
