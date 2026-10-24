"""Test module."""

import logging
import sys
from importlib.metadata import version

import pytest
import typer
from pyrig.rig.cli import subcommands as pyrig_subcommands_module
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pytest_mock import MockerFixture

from pyrig_runtime.core.dependencies.distribution import distribution_metadata
from pyrig_runtime.core.introspection.modules import safe_import_module
from pyrig_runtime.core.strings import kebab_to_snake_case
from pyrig_runtime.rig.cli import cli
from pyrig_runtime.rig.cli.cli import CLI, version_callback


def test_version_callback(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    """Test function."""
    mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
    assert version_callback(show=False) is False
    assert capsys.readouterr().out == ""

    with pytest.raises(typer.Exit):
        version_callback(show=True)
    assert capsys.readouterr().out == f"{version('pyrig-runtime')}\n"


class TestCLI:
    """Test class."""

    def test_base_app_kwargs(self, mocker: MockerFixture) -> None:
        """Test method."""
        project_name_mock = mocker.patch.object(
            CLI.I,
            CLI.project_name.__name__,
            return_value="pyrig-runtime",
        )
        kwargs = CLI.I.base_app_kwargs()
        project_name_mock.assert_called()
        assert kwargs == {
            "no_args_is_help": True,
            "help": PyprojectConfigFile().project_description(),
        }

    def test_register_subcommand_funcs(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        # fetch the live module: other tests may re-import it into sys.modules,
        # which would make the module-level reference stale for identity checks
        module = safe_import_module(pyrig_subcommands_module.__name__)
        app = CLI.I.base_app()
        CLI.I.register_subcommand_funcs(app=app, module=module)
        commands = {
            getattr(cmd.callback, "__name__")  # noqa: B009
            for cmd in app.registered_commands
            if cmd.callback is not None
        }
        # functions defined directly in the module become top-level commands
        assert {"sync"}.issubset(commands)
        # grouped commands are not registered as flat commands
        assert {"subcls", "cmd", "fixture"}.isdisjoint(commands)
        # nor are the group objects themselves registered as groups
        assert len(app.registered_groups) == 0

    def test_register_subcommand_groups(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        module = safe_import_module(pyrig_subcommands_module.__name__)
        app = CLI.I.base_app()
        CLI.I.register_subcommand_groups(app=app, module=module)
        groups = {group.name: group for group in app.registered_groups}
        assert "mk" in groups
        # only groups are registered, not flat commands
        assert len(app.registered_commands) == 0

    def test_package_name(self) -> None:
        """Test method."""
        assert CLI.I.package_name() == kebab_to_snake_case(CLI.I.project_name())

    def test_discovery_module(self) -> None:
        """Test method."""
        assert CLI.discovery_module() == cli

    def test_run(self, mocker: MockerFixture) -> None:
        """Test method."""
        run_mock = mocker.patch.object(CLI, CLI.app.__name__)
        CLI.I.run()
        run_mock.assert_called_once()

    def test_app(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        app = CLI.I.app()
        assert isinstance(app, typer.Typer)

    def test_base_app(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        base_app = CLI.I.base_app()
        assert isinstance(base_app, typer.Typer)

    def test_build_app(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        base_app = CLI.I.base_app()
        build_app = CLI.I.build_app(base_app)
        assert build_app is base_app

    def test_register_callback(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        app = CLI.I.base_app()
        CLI.I.register_callback(app)
        # check that the callback is registered
        assert app.registered_callback is not None

    def test_project_name(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        project_name = CLI.I.project_name()
        assert project_name == "pyrig-runtime"

        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime.exe"])
        project_name = CLI.I.project_name()
        assert project_name == "pyrig-runtime"

    def test_callback(self, mocker: MockerFixture) -> None:
        """Test method."""
        configure_logging_mock = mocker.patch.object(
            CLI.I,
            CLI.configure_logging.__name__,
        )
        CLI.I.callback()
        configure_logging_mock.assert_called()

    def test_configure_logging(self) -> None:
        """Test method."""
        # Test default (INFO level)
        CLI.I.configure_logging(verbose=0, quiet=0)
        assert logging.root.level == logging.INFO

        # Test quiet mode (WARNING level)
        CLI.I.configure_logging(verbose=1, quiet=2)
        assert logging.root.level == logging.WARNING

        # Test verbose mode (DEBUG level)
        CLI.I.configure_logging(verbose=3, quiet=2)
        assert logging.root.level == logging.DEBUG

        # Test very verbose mode (DEBUG level with module names)
        CLI.I.configure_logging(verbose=2, quiet=0)
        assert logging.root.level < logging.DEBUG

        # Test very verbose mode (DEBUG level with timestamps)
        CLI.I.configure_logging(verbose=3, quiet=0)
        assert logging.root.level < logging.DEBUG

    def test_register_subcommands(self, mocker: MockerFixture) -> None:
        """Test method."""
        project_name_mock = mocker.patch.object(
            CLI.I,
            CLI.project_name.__name__,
            return_value="pyrig",
        )
        app = CLI.I.base_app()
        CLI.I.register_subcommands(app)
        project_name_mock.assert_called()
        # flat commands are registered at the top level
        commands = {
            getattr(cmd.callback, "__name__")  # noqa: B009
            for cmd in app.registered_commands
            if cmd.callback is not None
        }
        assert {"sync"}.issubset(commands)
        # grouped commands are not registered at the top level
        assert {"cmd", "subcls"}.isdisjoint(commands)
        # the mk group is registered with its scaffold commands
        groups = {group.name: group for group in app.registered_groups}
        assert "mk" in groups
        mk_typer = groups["mk"].typer_instance
        assert mk_typer is not None
        mk_commands = {
            getattr(command.callback, "__name__")  # noqa: B009
            for command in mk_typer.registered_commands
            if command.callback is not None
        }
        assert {"cmd", "subcls"}.issubset(mk_commands)

        # a fresh app whose subcommands module fails to import gets no commands
        app = CLI.I.base_app()
        import_module_mock = mocker.patch(
            safe_import_module.__module__ + "." + safe_import_module.__name__,
            return_value=None,
        )
        CLI.I.register_subcommands(app)
        import_module_mock.assert_called_once()
        assert len(app.registered_commands) == 0

    def test_subcommand_groups(self) -> None:
        """Test method."""
        groups = CLI.I.subcommand_groups(pyrig_subcommands_module)
        assert "mk" in groups
        assert isinstance(groups["mk"], typer.Typer)

    def test_help_text(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        help_text = CLI.I.help_text()
        assert isinstance(help_text, str)
        assert len(help_text) > 0

        mocker.patch(
            cli.__name__ + "." + distribution_metadata.__name__,
            return_value=None,
        )
        assert CLI.I.help_text() == ""

    def test_merge_key(self) -> None:
        """Test method."""
        assert CLI.I.merge_key() == "CLI"

    def test_version(self, mocker: MockerFixture) -> None:
        """Test method."""
        mocker.patch.object(sys, "argv", ["/path/to/pyrig-runtime"])
        assert CLI.I.version() == version("pyrig-runtime")

    def test_subcommand_funcs(self) -> None:
        """Test method."""
        funcs = {
            getattr(func, "__name__")  # noqa: B009
            for func in CLI.I.subcommand_funcs(pyrig_subcommands_module)
        }
        assert "sync" in funcs
        assert {"subcls", "cmd", "fixture"}.isdisjoint(funcs)
