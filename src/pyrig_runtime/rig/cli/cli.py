"""Typer CLI application builder with extensible command discovery."""

import logging
import sys
from collections.abc import Callable, Hashable, Iterator
from importlib.metadata import distribution, version
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, override

import typer

from pyrig_runtime.core.dependencies.distribution import (
    distribution_metadata,
    distribution_summary,
)
from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.core.introspection.functions import module_funcs
from pyrig_runtime.core.introspection.modules import (
    replace_root_module,
)
from pyrig_runtime.core.strings import (
    kebab_to_snake_case,
    snake_to_kebab_case,
)
from pyrig_runtime.rig.cli import subcommands


def version_callback(*, show: bool) -> bool:
    """Print the invoking project's version and exit when requested.

    Args:
        show: Whether to display the project version and exit.

    Returns:
        The input value unchanged if version was not requested.

    Raises:
        typer.Exit: When `show` is `True`, after printing the project version.
    """
    if show:
        typer.echo(CLI.I.version())
        raise typer.Exit
    return show


class CLI(DependencySubclass):
    """Typer application builder for pyrig-runtime-based projects.

    Builds and runs the command-line application for any project that depends on
    pyrig-runtime. A dependent project may subclass `CLI` to override any step of
    the build to fit its needs.
    """

    @classmethod
    @override
    def discovery_module(cls) -> ModuleType:
        """Return this module, keeping subclass discovery scoped to it alone."""
        return sys.modules[__name__]

    @classmethod
    @override
    def merge_key(cls) -> Hashable:
        """Return a constant merge key.

        There is only one CLI so different subclasses should converge into
        a single subclass
        Returns:
            The name of this class: `CLI`.
        """
        return CLI.__name__

    def run(self) -> None:
        """Build and invoke the Typer application."""
        self.app()()

    def version(self) -> str:
        """Return the installed version of the invoking project."""
        return version(self.project_name())

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
        return typer.Typer(**self.base_app_kwargs())

    def build_app(self, app: typer.Typer) -> typer.Typer:
        """Register the callback and all commands onto the given app.

        Args:
            app: The Typer app to populate.

        Returns:
            The same app instance, now fully configured.
        """
        self.register_callback(app)
        self.register_subcommands(app)
        return app

    def base_app_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments for creating the base Typer application.

        This base configuration makes sure that calling the CLI without
        any arguments will display the help message, and that the help text
        is the same as the description of the invoking project.

        Returns:
            A dictionary of keyword arguments to pass to `typer.Typer`.
        """
        return {
            "no_args_is_help": True,
            "help": self.help_text(),
        }

    def register_callback(self, app: typer.Typer) -> None:
        """Attach the version and verbosity options to the given app.

        Args:
            app: The Typer app to attach the callback to.
        """
        app.callback()(self.callback)

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
        subcommands_module = replace_root_module(
            subcommands,
            root=self.package_name(),
            default=None,
        )

        if subcommands_module is None:
            return

        self.register_subcommand_funcs(app=app, module=subcommands_module)
        self.register_subcommand_groups(app=app, module=subcommands_module)

    def callback(
        self,
        *,
        _version: Annotated[
            bool,
            typer.Option(
                "--version",
                callback=version_callback,
                is_eager=True,
                help="Show the version and exit.",
            ),
        ] = False,
        verbose: Annotated[
            int,
            typer.Option(
                "--verbose",
                "-v",
                count=True,
                help="Increase verbosity: -v (DEBUG), -vv (modules), -vvv (timestamps)",
            ),
        ] = 0,
        quiet: Annotated[
            int,
            typer.Option(
                "--quiet",
                "-q",
                count=True,
                help="Decrease verbosity: -q (WARNING), -qq (ERROR), -qqq (CRITICAL)",
            ),
        ] = 0,
    ) -> None:
        """Apply the verbosity options for the current invocation.

        Args:
            _version: Handled by the eager version option callback.
            verbose: Number of times verbosity was increased (e.g. via `-v`).
            quiet: Number of times verbosity was decreased (e.g. via `-q`).
        """
        self.configure_logging(verbose, quiet)

    def help_text(self) -> str:
        """Return the help text for the invoking project.

        Returns:
            The project's distribution summary, or an empty string if no
            metadata is available for it.
        """
        metadata = distribution_metadata(
            distribution(self.project_name()),
        )
        if metadata is None:
            return ""
        return distribution_summary(metadata)

    def package_name(self) -> str:
        """Return the snake_case package name of the invoking project.

        For example, if the project is invoked as `uv run my-project`, the
        package name is `my_project`.
        """
        return kebab_to_snake_case(self.project_name())

    def register_subcommand_funcs(
        self,
        app: typer.Typer,
        module: ModuleType,
    ) -> None:
        """Register every function defined in a module as a top-level command.

        Adds each function found directly in `module` to `app` as a flat Typer
        command. Imported functions are excluded.

        Args:
            app: The Typer app to register the commands onto.
            module: The subcommands module to scan for command functions.
        """
        for func in self.subcommand_funcs(module):
            app.command()(func)

    def register_subcommand_groups(self, app: typer.Typer, module: ModuleType) -> None:
        """Register every `typer.Typer` instance in a module as a named command group.

        Attaches each `typer.Typer` found in the module's namespace to `app`,
        using the kebab-case form of the attribute name as the group name.

        Args:
            app: The Typer app to register the command groups onto.
            module: The subcommands module to scan for group instances.
        """
        for name, group in self.subcommand_groups(module).items():
            app.add_typer(group, name=name)

    def configure_logging(self, verbose: int, quiet: int) -> None:
        """Configure the logging level and format for the current invocation.

        Each increment of `verbose` lowers the log level by one step (toward
        DEBUG); each increment of `quiet` raises it by one step (toward
        CRITICAL). The message format also expands as `verbose` increases:
        the level name is added first, then the module name, then a
        timestamp.

        The resulting level is not clamped to the standard range, so a high
        enough `verbose` or `quiet` count can push it below `DEBUG` or above
        `CRITICAL`.

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

        verbose_names = 1
        verbose_modules = verbose_names + 1
        verbose_timestamps = verbose_modules + 1

        if verbose >= verbose_timestamps:
            fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        elif verbose == verbose_modules:
            fmt = "%(levelname)s [%(name)s] %(message)s"
        elif verbose == verbose_names:
            fmt = "%(levelname)s: %(message)s"
        else:
            fmt = "%(message)s"

        logging.basicConfig(level=level, format=fmt, force=True)

    def project_name(self) -> str:
        """Return the stem of `sys.argv[0]` as the invoking project name.

        When a project is invoked through a registered console-script entry point
        (e.g. `uv run my-project`), `sys.argv[0]` is the path to that script, so
        its stem is the project name as it was registered.
        """
        return Path(sys.argv[0]).stem

    def subcommand_funcs(self, module: ModuleType) -> Iterator[Callable[..., Any]]:
        """Return the functions defined directly in a subcommands module.

        Imported functions are excluded.

        Args:
            module: The subcommands module to scan.

        Returns:
            Iterator of functions defined directly in the module.
        """
        return module_funcs(module)

    def subcommand_groups(self, module: ModuleType) -> dict[str, typer.Typer]:
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
