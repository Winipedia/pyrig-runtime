"""Test module."""

import os
import sys

import pyrig
from pyrig import core as pyrig_core

import pyrig_runtime
from pyrig_runtime import core, rig
from pyrig_runtime.core.introspection.modules import (
    import_modules,
    iter_modules,
    replace_root_module,
    replace_root_module_name,
    root_module,
    root_module_name,
    safe_import_module,
)
from pyrig_runtime.rig import cli
from pyrig_runtime.rig.cli import subcommands


def test_import_modules() -> None:
    """Test function."""
    names = ["sys", "os"]
    modules = tuple(import_modules(names))

    assert modules == (sys, os)


def test_iter_modules() -> None:
    """Test function."""
    modules = tuple(iter_modules(package=rig))
    assert (cli, True) in modules

    cli_modules = tuple(iter_modules(package=cli))
    assert (subcommands, False) in cli_modules


def test_replace_root_module() -> None:
    """Test function."""
    result = replace_root_module(pyrig_runtime, "sys", default=None)
    assert result is sys

    assert (
        replace_root_module(pyrig_runtime, "nonexistent", default="default")
        == "default"
    )
    assert replace_root_module(pyrig_runtime, "nonexistent", default=None) is None

    assert replace_root_module(core, pyrig.__name__) is pyrig_core


def test_replace_root_module_name() -> None:
    """Test function."""
    assert replace_root_module_name(core.__name__, pyrig.__name__) == "pyrig.core"
    assert replace_root_module_name(pyrig_runtime.__name__, "sys") == "sys"


def test_root_module() -> None:
    """Test function."""
    assert root_module(subcommands) is pyrig_runtime


def test_root_module_name() -> None:
    """Test function."""
    assert root_module_name(pyrig_runtime.__name__) == "pyrig_runtime"
    assert root_module_name(core.__name__) == "pyrig_runtime"
    assert root_module_name(sys.__name__) == "sys"
    assert root_module_name(core.__name__) == "pyrig_runtime"
    assert root_module_name(pyrig_core.__name__) == "pyrig"


def test_safe_import_module() -> None:
    """Test function."""
    # Test importing a valid module
    result = safe_import_module("sys")
    assert result.__name__ == "sys", f"Expected sys module, got {result}"

    # Test importing a non-existent module with a default
    result = safe_import_module("nonexistent", default="default")
    assert result == "default", f"Expected default, got {result}"
