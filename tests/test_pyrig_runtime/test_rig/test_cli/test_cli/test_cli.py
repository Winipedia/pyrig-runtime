"""Test module."""

import logging

import typer
from pyrig.rig.cli import subcommands as pyrig_subcommands_module
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pytest_mock import MockerFixture

from pyrig_runtime.core.introspection.modules import safe_import_module
from pyrig_runtime.core.strings import kebab_to_snake_case
from pyrig_runtime.rig.cli import cli as cli_package
from pyrig_runtime.rig.cli.cli import cli as cli_module
from pyrig_runtime.rig.cli.cli.cli import CLI


class TestCLI:
    """Test class."""

    def test_base_app_kwargs(self, mocker: MockerFixture) -> None:
        """Test method."""
        project_name_mock = mocker.patch.object(
            CLI.I, CLI.project_name.__name__, return_value="pyrig-runtime"
        )
        kwargs = CLI.I.base_app_kwargs()
        project_name_mock.assert_called()
        assert kwargs == {
            "no_args_is_help": True,
            "help": PyprojectConfigFile().project_description(),
        }

    def test_register_direct_subcommands(self) -> None:
        """Test method."""
        # fetch the live module: other tests may re-import it into sys.modules,
        # which would make the module-level reference stale for identity checks
        module = safe_import_module(pyrig_subcommands_module.__name__)
        app = CLI.I.base_app()
        CLI.I.register_direct_subcommands(app=app, module=module)
        commands = {cmd.callback.__name__ for cmd in app.registered_commands}
        # functions defined directly in the module become top-level commands
        assert {"sync"}.issubset(commands)
        # grouped commands are not registered as flat commands
        assert {"subcls", "cmd", "fixture"}.isdisjoint(commands)
        # nor are the group objects themselves registered as groups
        assert len(app.registered_groups) == 0

    def test_register_subcommand_groups(self) -> None:
        """Test method."""
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

    def test_dependency_package(self) -> None:
        """Test method."""
        assert CLI.dependency_package() == cli_package

    def test_run(self, mocker: MockerFixture) -> None:
        """Test method."""
        run_mock = mocker.patch.object(CLI, CLI.app.__name__)
        CLI.I.run()
        run_mock.assert_called_once()

    def test_app(self) -> None:
        """Test method."""
        app = CLI.I.app()
        assert isinstance(app, typer.Typer)

    def test_base_app(self) -> None:
        """Test method."""
        base_app = CLI.I.base_app()
        assert isinstance(base_app, typer.Typer)

    def test_build_app(self) -> None:
        """Test method."""
        base_app = CLI.I.base_app()
        build_app = CLI.I.build_app(base_app)
        assert build_app is base_app

    def test_register_callback(self) -> None:
        """Test method."""
        app = CLI.I.base_app()
        CLI.I.register_callback(app)
        # check that the callback is registered
        assert app.registered_callback is not None

    def test_project_name(self) -> None:
        """Test method."""
        project_name = CLI.I.project_name()
        assert isinstance(project_name, str)
        assert len(project_name) > 0

    def test_callback(self, mocker: MockerFixture) -> None:
        """Test method."""
        configure_logging_mock = mocker.patch.object(
            CLI.I, CLI.configure_logging.__name__
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
            CLI.I, CLI.project_name.__name__, return_value="pyrig"
        )
        app = CLI.I.base_app()
        CLI.I.register_subcommands(app)
        project_name_mock.assert_called()
        # flat commands are registered at the top level
        commands = {cmd.callback.__name__ for cmd in app.registered_commands}
        assert {"sync"}.issubset(commands)
        # grouped commands are not registered at the top level
        assert {"cmd", "subcls"}.isdisjoint(commands)
        # the mk group is registered with its scaffold commands
        groups = {group.name: group for group in app.registered_groups}
        assert "mk" in groups
        mk_commands = {
            command.callback.__name__
            for command in groups["mk"].typer_instance.registered_commands
        }
        assert {"cmd", "subcls"}.issubset(mk_commands)

        # a fresh app whose subcommands module fails to import gets no commands
        app = CLI.I.base_app()
        import_module_mock = mocker.patch(
            cli_module.__name__ + "." + safe_import_module.__name__,
            return_value=None,
        )
        CLI.I.register_subcommands(app)
        import_module_mock.assert_called_once()
        assert len(app.registered_commands) == 0

    def test_register_shared_subcommands(self) -> None:
        """Test method."""
        app = CLI.I.base_app()
        CLI.I.register_shared_subcommands(app)
        # check that version is in the app commands
        commands = {cmd.callback.__name__ for cmd in app.registered_commands}
        assert {"version"}.issubset(commands)

    def test_module_subcommand_groups(self) -> None:
        """Test method."""
        groups = CLI.I.module_subcommand_groups(pyrig_subcommands_module)
        assert "mk" in groups
        assert isinstance(groups["mk"], typer.Typer)
