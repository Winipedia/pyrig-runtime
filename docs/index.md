# pyrig-runtime Documentation

<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-runtime/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig-runtime/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-runtime/deploy.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig-runtime/actions/workflows/deploy.yml)
<!-- testing -->
[![CoverageTester](https://codecov.io/gh/Winipedia/pyrig-runtime/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig-runtime)
[![ProjectTester](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org)
<!-- code-quality -->
[![DependencyAuditor](https://img.shields.io/badge/security-pip--audit-blue?logo=python)](https://github.com/pypa/pip-audit)
[![DependencyChecker](https://img.shields.io/badge/dependencies-deptry-blue)](https://github.com/osprey-oss/deptry)
[![MarkdownLinter](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SecurityChecker](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![SpellChecker](https://img.shields.io/badge/spell--check-typos-blue)](https://github.com/crate-ci/typos)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![VersionControlHookManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
<!-- tooling -->
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pyrigger](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig-runtime?style=social)](https://github.com/Winipedia/pyrig-runtime)
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
<!-- project-info -->
[![DocsBuilder](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://Winipedia.github.io/pyrig-runtime)
[![PackageIndex](https://img.shields.io/pypi/v/pyrig-runtime?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig-runtime)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig-runtime)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig-runtime)](https://github.com/Winipedia/pyrig-runtime/blob/main/LICENSE)

---

> Runtime dependency and library for projects built with pyrig.

---

## Overview

`pyrig-runtime` is the runtime layer that projects built with
[pyrig](https://github.com/Winipedia/pyrig) depend on. It bundles the
capabilities those projects rely on while they run.

It is a standalone library — its only dependency is
[Typer](https://typer.tiangolo.com), and nothing here requires pyrig itself to
be installed. pyrig is the build- and development-time toolkit; pyrig-runtime is
the piece that ships with the projects pyrig creates.

## Installation

In most cases you do not install it directly as pyrig adds it to a project's
dependencies for you when you initialize a project with it.
But if you for example want to use the plugin discovery for your own interests you
can add it like any other python package:

```bash
uv add pyrig-runtime
# or
pip install pyrig-runtime
```

## Features

pyrig-runtime provides two main capabilities. Each has its own page with more
detail:

- **[Plugin discovery](plugins.md)** — define a base class and its
  subclasses are discovered automatically across every installed package that
  depends on it, with no registration step..
- **[Automatic CLI](cli.md)** — every project gets a working
  command-line interface.

## API reference

Every public module, class, and function is documented from its source in the
[API reference](api.md).
