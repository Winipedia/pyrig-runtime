# Automatic CLI

Every project built with pyrig gets a working command-line interface for free.
The CLI is a [Typer](https://typer.tiangolo.com) application that assembles
itself at startup, so you get a runnable entry point without wiring anything
up — and you can extend it with your own commands.

## The entry point

A project gets its CLI from a console script that points to pyrig-runtime's
entry point. pyrig adds this for you, but it is just a normal script entry in
`pyproject.toml`:

```toml
[project.scripts]
my-project = "pyrig_runtime.rig.cli.main:main"
```

Running the script builds the Typer application and dispatches the requested
command. The invoking project is detected from the name of the script that
launched it (`my-project` above); converted to snake_case (`my_project`),
that name is where the project's own commands are loaded from.

`-v` / `-q` adjust logging verbosity. Something like `-vv` or `-qqq` or
even `-vqqvqvq` are also possible.

## Adding your own commands

Define commands in your project's `my_project.rig.cli.subcommands` module:

- every **function** defined directly there becomes a top-level command;
- every module-level **`typer.Typer`** instance becomes a command group, named
  after its variable in kebab-case.

```python
# src/my_project/rig/cli/subcommands.py
def greet(name: str) -> None:
    """Greet someone."""
    print(f"hello {name}")
```

```bash
$ uv run my-project greet world
hello world
```

## Customizing the build

The application is built by a `CLI` class, which is itself a
[discoverable plugin](plugins.md). Define a subclass in your project's
`my_project.rig.cli.cli` module to override any step of the build — the
most-derived subclass is used automatically.

## Version

Every project's CLI provides a root-level `--version` option that prints
the invoking project's installed version and exits successfully:

```bash
$ uv run my-project --version
1.2.3
```

The project must be installed. The option is eager: it exits before the normal
logging callback or command executes, and does not require a subcommand.
Application construction and plugin discovery still happen before option parsing.
Override `CLI.version()` to customize version lookup.
