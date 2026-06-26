"""Typer CLI application builder with cross-package command discovery."""

import logging
import sys
from itertools import chain
from pathlib import Path
from types import ModuleType

import typer

from pyrig_runtime.core.dependencies.discovery import (
    discover_equivalent_modules_across_dependents,
)
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.introspection.functions import module_functions
from pyrig_runtime.core.introspection.modules import (
    import_module_with_default,
    replace_root_module_name,
)
from pyrig_runtime.core.strings import kebab_to_snake_case, snake_to_kebab_case
from pyrig_runtime.rig.cli import cli, shared_subcommands, subcommands


class CLI(DependencySubclass):
    """Typer application builder for pyrig-runtime-based projects.

    Builds and runs the command-line application for any project that depends on
    pyrig-runtime. A dependent project may subclass `CLI` to override any step of
    the build to fit its needs.
    """

    @classmethod
    def dependency_package(cls) -> ModuleType:
        """Return the `pyrig_runtime.rig.cli.cli` package module."""
        return cli

    def run(self) -> None:
        """Build and invoke the Typer application."""
        self.app()()

    def app(self) -> typer.Typer:
        """Build a fully configured Typer application."""
        app = self.base_app()
        return self.build_app(app)

    def base_app(self) -> typer.Typer:
        """Create an empty base Typer application.

        Returns:
            A new Typer app configured to show help when invoked without
            arguments.
        """
        return typer.Typer(no_args_is_help=True)

    def build_app(self, app: typer.Typer) -> typer.Typer:
        """Register the callback and all commands onto the given app.

        Args:
            app: The Typer app to populate.

        Returns:
            The same app instance, now fully configured.
        """
        self.register_callback(app)
        self.register_subcommands(app)
        self.register_shared_subcommands(app)
        return app

    def register_callback(self, app: typer.Typer) -> None:
        """Attach the verbosity callback to the given app.

        Args:
            app: The Typer app to attach the callback to.
        """
        app.callback()(self.callback)

    def callback(
        self,
        verbose: int = typer.Option(
            0,
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity: -v (DEBUG), -vv (modules), -vvv (timestamps)",
        ),
        quiet: int = typer.Option(
            0,
            "--quiet",
            "-q",
            count=True,
            help="Decrease verbosity: -q (WARNING), -qq (ERROR), -qqq (CRITICAL)",
        ),
    ) -> None:
        # cli is inherited by dependent projects, so the callback docstring is
        # intentionally left blank to avoid confusion in help messages
        """"""  # noqa: D419
        self.configure_logging(verbose, quiet)

    def configure_logging(self, verbose: int, quiet: int) -> None:
        """Configure the logging level and format for the current invocation.

        Each increment of `verbose` lowers the log level by one step (toward
        DEBUG); each increment of `quiet` raises it by one step (toward
        CRITICAL). The format also expands at higher verbosity, adding module
        names at two increments and timestamps at three.

        Args:
            verbose: Number of times verbosity was increased (e.g. via `-v`).
            quiet: Number of times verbosity was decreased (e.g. via `-q`).

        Note:
            Uses `logging.basicConfig` with `force=True` to ensure that the
            configuration is applied even if logging has already been configured
            by the calling project or other dependencies.
        """
        level = logging.INFO
        step = logging.INFO - logging.DEBUG
        level -= step * verbose
        level += step * quiet

        verbose_timestamps = 3
        verbose_modules = 2

        if verbose >= verbose_timestamps:
            fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        elif verbose == verbose_modules:
            fmt = "%(levelname)s [%(name)s] %(message)s"
        elif verbose == 1:
            fmt = "%(levelname)s: %(message)s"
        else:
            fmt = "%(message)s"

        logging.basicConfig(level=level, format=fmt, force=True)

    def register_subcommands(self, app: typer.Typer) -> None:
        """Discover and register project-specific commands for the invoking project.

        Any dependent project can define its own CLI commands by adding
        functions or `typer.Typer` groups to `<package>.rig.cli.subcommands`.

        Args:
            app: The Typer app to register the commands onto.

        Note:
            If the invoking project's subcommands module cannot be imported,
            registration is silently skipped.
        """
        subcommands_module_name = replace_root_module_name(
            subcommands, root_module_name=self.package_name()
        )
        subcommands_module = import_module_with_default(subcommands_module_name)

        if subcommands_module is None:
            return

        self.register_direct_subcommands(app=app, module=subcommands_module)
        self.register_subcommand_groups(app=app, module=subcommands_module)

    def register_shared_subcommands(self, app: typer.Typer) -> None:
        """Discover and register shared commands from pyrig-runtime and its dependents.

        Args:
            app: The Typer app to register the commands onto.

        Note:
            Commands are registered in dependency order (pyrig-runtime first,
            then dependent packages in topological order). When two packages
            define a command with the same name, the last registration takes
            precedence.
        """
        for shared_subcommands_module in chain(
            (shared_subcommands,),
            discover_equivalent_modules_across_dependents(
                shared_subcommands,
            ),
        ):
            self.register_direct_subcommands(app=app, module=shared_subcommands_module)
            self.register_subcommand_groups(app=app, module=shared_subcommands_module)

    def register_direct_subcommands(self, app: typer.Typer, module: ModuleType) -> None:
        """Register every function defined in a module as a top-level command.

        Adds each function found directly in `module` to `app` as a flat Typer
        command. Imported functions are excluded.

        Args:
            app: The Typer app to register the commands onto.
            module: The subcommands module to scan for command functions.
        """
        for func in module_functions(module):
            app.command()(func)

    def register_subcommand_groups(self, app: typer.Typer, module: ModuleType) -> None:
        """Register every `typer.Typer` instance in a module as a named command group.

        Attaches each `typer.Typer` found in the module's namespace to `app`,
        using the kebab-case form of the attribute name as the group name.

        Args:
            app: The Typer app to register the command groups onto.
            module: The subcommands module to scan for group instances.
        """
        for name, group in self.module_subcommand_groups(module).items():
            app.add_typer(group, name=name)

    def module_subcommand_groups(self, module: ModuleType) -> dict[str, typer.Typer]:
        """Return the Typer command groups found in a subcommands module.

        Scans the module's namespace for `typer.Typer` instances. Both natively
        defined and imported instances are included. The key for each entry is
        the kebab-case form of the attribute name it is bound to.

        Args:
            module: The subcommands module to scan.

        Returns:
            Mapping of kebab-case attribute name to the `typer.Typer` instance
            bound to it.
        """
        return {
            snake_to_kebab_case(name): obj
            for name, obj in vars(module).items()
            if isinstance(obj, typer.Typer)
        }

    def package_name(self) -> str:
        """Return the snake_case package name of the invoking project.

        For example, if the project is invoked as `uv run my-project`, the
        package name is `my_project`.
        """
        return kebab_to_snake_case(self.project_name())

    def project_name(self) -> str:
        """Return the basename of `sys.argv[0]` as the invoking project name.

        When a project is invoked through a registered console-script entry point
        (e.g. `uv run my-project`), `sys.argv[0]` is the path to that script, so
        its basename is the project name as it was registered.
        """
        return Path(sys.argv[0]).name
