"""Explicit references for reviewed dead code false positives."""

from _typeshed import SupportsRichComparison

from pyrig_runtime.core.dependencies.subclass import DependencySubclass
from pyrig_runtime.rig.cli.main import main

_ENTRY_POINTS = (main,)

_LIBRARY_USAGES = (
    DependencySubclass.__str__,
    DependencySubclass.concrete_leaves,
    DependencySubclass.sorted_subclasses,
)
_TYPE_CHECKING = (SupportsRichComparison,)
