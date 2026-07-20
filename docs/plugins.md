# Plugin Discovery

Plugin discovery lets you define a base class and have all of its subclasses
found automatically across your own package and every installed package that
depends on it with no registry, no entry points, and no manual imports.

## Declaring a base class

Subclass `DependencySubclass` and implement `discovery_module()`, a classmethod
that returns the module or package that scopes where implementations live:

```python
# my_project/plugins/base/plugin.py
from abc import abstractmethod
from types import ModuleType

from pyrig_runtime.core.dependencies.subclass import DependencySubclass

import my_project.plugins


class Plugin(DependencySubclass):
    @classmethod
    def discovery_module(cls) -> ModuleType:
        return my_project.plugins

    @abstractmethod
    def run(self) -> str:
        """Return this plugin's result."""
```

The returned module scopes discovery. Discovery looks for subclasses whose
defining module name starts with the returned module's name, both in your own
distribution **and** at the same sub-path inside every installed package that
depends on its root package — so a dependent package contributes plugins by
mirroring the path (for example, `otherpkg.plugins`).

Return a **package** to widen discovery to its whole module hierarchy, which is
imported and searched recursively. Return a **plain module** to keep discovery
narrow, limiting it to that single file.

## Defining implementations

Put concrete subclasses in any module covered by the declared scope:

```python
# my_project/plugins/greeting.py
from my_project.plugins.base import Plugin


class Greeting(Plugin):
    def run(self) -> str:
        return "hello"
```

You never import or register them anywhere. When the scope is a package it is
traversed recursively, so it does not matter how deeply a module or class is
nested — every module under the package, at any depth, is imported as a side
effect, and simply defining the class is enough for it to be found. When the
scope is a plain module, define the subclass in that module (or one whose name
shares its prefix).

## Discovering and using subclasses

| Accessor | Returns |
| --- | --- |
| `Plugin.subclasses()` | Every leaf subclass found across the dependency graph (intermediate base classes are dropped). |
| `Plugin.concrete_subclasses()` | The same as `Plugin.subclasses()`, excluding abstract classes from the returned result. |
| `Plugin.sorted_subclasses(subclasses)` | A given iterable of subclasses ordered by `sort_key()`. |
| `Plugin.L` | The single leaf subclass — or the class itself if none exist. Raises if more than one leaf is found. |
| `Plugin.I` | A cached instance of `Plugin.L`. |

```python
for plugin in Plugin.concrete_subclasses():
    ...

result = Plugin.I.run()  # call the one active implementation
```

## Ordering

Across packages, subclasses are discovered in dependency order — a package is
processed before the packages that depend on it. Within a single package the
order is not guaranteed. When you need a deterministic order, override
`sort_key()` and iterate with `sorted_subclasses()`.

## A single active implementation

`L` and `I` are for hierarchies that are meant to have exactly one active
implementation: the most-derived (leaf) subclass wins, which lets a dependent
package override a base implementation simply by subclassing it. If two
unrelated leaves are found, `L` raises — that ambiguity is treated as a
configuration error that must be resolved.

## Resolving conflicts

Call the active implementation through `I`. With only the base `Greeting`
defined, it is the single leaf, so this works:

```python
Greeting.I.run()  # "hello"
```

Now suppose two installed packages each override `Greeting`:

```python
# plugin_one/plugins/greeting.py
from my_project.plugins.greeting import Greeting


class GreetingOne(Greeting):
    def run(self) -> str:
        return "hi"
```

```python
# plugin_two/plugins/greeting.py
from my_project.plugins.greeting import Greeting


class GreetingTwo(Greeting):
    def run(self) -> str:
        return "hey"
```

With both installed, `Greeting` has two leaf subclasses, so `Greeting.I` (and
`Greeting.L`) raises — the active implementation is ambiguous.

Resolve it in a package that depends on both by defining a class that inherits
from each conflicting leaf. It becomes the single most-derived leaf, so
discovery picks it unambiguously:

```python
# my_other_project/plugins/greeting.py
from plugin_one.plugins.greeting import GreetingOne
from plugin_two.plugins.greeting import GreetingTwo


class GreetingResolved(GreetingOne, GreetingTwo):
    def run(self) -> str:
        # combine both behaviors however you like
        return GreetingOne.run(self) + GreetingTwo.run(self)
```

```python
Greeting.I.run()  # "hihey" — GreetingResolved combines both
```

## See also

- [Automatic CLI](cli.md) — built on this discovery mechanism.
- [API reference](api.md) — full signatures for every accessor above.
