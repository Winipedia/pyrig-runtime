# pyrig-runtime

<!-- project-status -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-runtime/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig-runtime/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig-runtime/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig-runtime/actions/workflows/release.yml)
[![ProjectTester](https://codecov.io/gh/Winipedia/pyrig-runtime/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig-runtime)
<!-- code-quality -->
[![ByteOrderMarkerFormatter](https://img.shields.io/badge/BOM-fix--byte--order--marker-orange)](https://prek.j178.dev/reference/built-in-hooks/#fix-byte-order-marker)
[![CICDLinter](https://img.shields.io/badge/CI/CD-actionlint-blue)](https://github.com/rhysd/actionlint)
[![CICDSecurityChecker](https://img.shields.io/badge/%F0%9F%8C%88-zizmor-white?labelColor=white)](https://github.com/zizmorcore/zizmor)
[![CaseConflictChecker](https://img.shields.io/badge/case--conflict-check--case--conflict-blue)](https://prek.j178.dev/reference/built-in-hooks/#check-case-conflict)
[![DeadCodeChecker](https://img.shields.io/badge/dead--code-vulture-blue)](https://github.com/jendrikseipp/vulture)
[![DependencyChecker](https://img.shields.io/badge/dependencies-deptry-blue)](https://github.com/osprey-oss/deptry)
[![EndOfFileFormatter](https://img.shields.io/badge/EOF-end--of--file--fixer-orange)](https://prek.j178.dev/reference/built-in-hooks/#end-of-file-fixer)
[![EndOfLineFormatter](https://img.shields.io/badge/EOL-mixed--line--ending-orange)](https://prek.j178.dev/reference/built-in-hooks/#mixed-line-ending)
[![JSONFormatter](https://img.shields.io/badge/JSON-pretty--format--json-orange)](https://prek.j178.dev/reference/built-in-hooks/#pretty-format-json)
[![JSONLinter](https://img.shields.io/badge/JSON-check--json-blue)](https://prek.j178.dev/reference/built-in-hooks/#check-json)
[![LargeFileChecker](https://img.shields.io/badge/large--files-check--added--large--files-blue)](https://prek.j178.dev/reference/built-in-hooks/#check-added-large-files)
[![MarkdownLinter](https://img.shields.io/badge/Markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![MergeConflictChecker](https://img.shields.io/badge/merge--conflict-check--merge--conflict-blue)](https://prek.j178.dev/reference/built-in-hooks/#check-merge-conflict)
[![ModuleTestNamingChecker](https://img.shields.io/badge/test--naming-name--tests--test-blue)](https://github.com/pre-commit/pre-commit-hooks#name-tests-test)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SecretsChecker](https://img.shields.io/badge/secrets-detect--secrets-blue)](https://github.com/Yelp/detect-secrets)
[![SecurityChecker](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![ShellFormatter](https://img.shields.io/badge/shell-shfmt-orange)](https://github.com/mvdan/sh)
[![ShellLinter](https://img.shields.io/badge/shell-shellcheck-blue)](https://github.com/koalaman/shellcheck)
[![SpellChecker](https://img.shields.io/badge/spell--check-typos-blue)](https://github.com/crate-ci/typos)
[![TOMLLinter](https://img.shields.io/badge/TOML-tombi-blueviolet)](https://github.com/tombi-toml/tombi)
[![TrailingWhitespaceFormatter](https://img.shields.io/badge/whitespace-trailing--whitespace-orange)](https://prek.j178.dev/reference/built-in-hooks/#trailing-whitespace)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![YAMLLinter](https://img.shields.io/badge/YAML-ryl-red)](https://github.com/owenlamont/ryl)
<!-- tooling -->
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pyrigger](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Winipedia/pyrig/main/docs/assets/badge.json)](https://github.com/Winipedia/pyrig)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig-runtime?style=social)](https://github.com/Winipedia/pyrig-runtime)
[![VersionControlHookManager](https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge.svg)](https://github.com/j178/prek)
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
<!-- project-info -->
[![DocsBuilder](https://img.shields.io/badge/Documentation-zensical-326CE5)](https://Winipedia.github.io/pyrig-runtime)
[![PackageIndex](https://img.shields.io/pypi/v/pyrig-runtime?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig-runtime)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig-runtime)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig-runtime)](https://github.com/Winipedia/pyrig-runtime/blob/main/LICENSE)

---

> Plugin system and CLI engine for projects built with pyrig.

---

## Overview

Put simply, pyrig-runtime is a plugin system based on classes that declare
functionality through code, and via subclassing these classes any state and
functionality can be changed, removed or extended by overriding the methods
of parent classes. For pyrig-runtime itself this applies to the CLI class it provides.

`pyrig-runtime` was built for [pyrig](https://github.com/Winipedia/pyrig) which
uses it for its file generation and tool wrapping classes and its CLI.
pyrig-runtime is a standalone library — its only dependency is Typer, and nothing
here requires pyrig itself to be installed. pyrig is a development dependency and
dev toolkit; pyrig-runtime is a plugin system and automatic CLI enabler.

## Features

- **Plugin discovery via classes** — define a base class and its subclasses are
  discovered automatically across every installed package that depends on it without
  the need for registration. [Learn more](https://Winipedia.github.io/pyrig-runtime/plugins).
- **Automatic CLI** — every project gets a working command-line interface,
  assembled from commands across its dependencies.
  [Learn more](https://Winipedia.github.io/pyrig-runtime/cli).

## Documentation

For anything beyond this overview, see the [Documentation](https://Winipedia.github.io/pyrig-runtime).
