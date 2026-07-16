"""Test module."""

import os
import sys
from contextlib import chdir
from pathlib import Path

import pyrig
from pyrig import core as pyrig_core
from pyrig.core.introspection.modules import import_module_with_file_fallback

import pyrig_runtime
from pyrig_runtime import core
from pyrig_runtime.core.introspection.modules import (
    import_modules,
    iter_modules,
    replace_root_module,
    replace_root_module_name,
    root_module,
    root_module_name,
    safe_import_module,
)
from pyrig_runtime.rig.cli import subcommands


def test_root_module() -> None:
    """Test function."""
    assert root_module(subcommands) is pyrig_runtime


def test_safe_import_module() -> None:
    """Test function."""
    # Test importing a valid module
    result = safe_import_module("sys")
    assert result.__name__ == "sys", f"Expected sys module, got {result}"

    # Test importing a non-existent module with a default
    result = safe_import_module("nonexistent", default="default")
    assert result == "default", f"Expected default, got {result}"


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


def test_import_modules() -> None:
    """Test function."""
    names = ["sys", "os"]
    modules = tuple(import_modules(names))

    assert modules == (sys, os)


def test_iter_modules(tmp_path: Path) -> None:
    """Test function."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / test_iter_modules.__name__
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        module_file = package_dir / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        package = import_module_with_file_fallback(
            package_dir,
            name=test_iter_modules.__name__,
        )

        modules = iter_modules(package)
        modules_names = [m.__name__ for m, _ in modules]
        assert modules_names == [package.__name__ + ".test_module"], (
            f"Expected [package.test_module], got {modules}"
        )


def test_replace_root_module_name() -> None:
    """Test function."""
    assert replace_root_module_name(core, pyrig.__name__) == "pyrig.core"
    assert replace_root_module_name(pyrig_runtime, "sys") == "sys"


def test_root_module_name() -> None:
    """Test function."""
    assert root_module_name(pyrig_runtime) == "pyrig_runtime"
    assert root_module_name(core) == "pyrig_runtime"
    assert root_module_name(sys) == "sys"
    assert root_module_name(core) == "pyrig_runtime"
    assert root_module_name(pyrig_core) == "pyrig"
