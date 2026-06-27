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
command. The invoking project is detected automatically, so its commands are
loaded.

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
[discoverable plugin](plugins.md). A project can subclass it to override
any step of the build — the most-derived subclass is used automatically.

## Shared commands

A shared command is available in **every** project that depends on pyrig-runtime,
not just the package that defines it. The built-in `version` command is one: it
is defined by pyrig-runtime, so every dependent project has it:

```bash
$ uv run my-project version
my-project 1.2.3
```

You can add your own. Define shared commands in your project's
`my_project.rig.cli.shared_subcommands` module:

```python
# src/my_project/rig/cli/shared_subcommands.py
def version2() -> None:
    """Print the version a different way."""
    ...
```

Once `my_project` is installed in an environment, `version2` is available from every
project in that environment that depends on pyrig-runtime — including
pyrig-runtime's own CLI and any other dependent project, not only `my_project`:

```bash
uv run pyrig-runtime version2
uv run otherproject version2
```

When two packages define a shared command with the same name, the one registered
last (in dependency order) wins, so a dependent package can override a built-in.
This is simply Typer's default behaviour.

## See also

- [Plugin discovery](plugins.md) — the mechanism the CLI is built on.
- [API reference](api.md) — full signatures for the CLI builder and commands.
