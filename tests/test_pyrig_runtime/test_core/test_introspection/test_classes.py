"""Test module."""

from abc import ABC, abstractmethod
from typing import ClassVar

import pytest

from pyrig_runtime.core.introspection.classes import (
    discover_subclasses,
    filter_concrete_classes,
    filter_leaf_classes,
    generate_class,
)


# Test classes for cls_methods
class ParentClass:
    """Parent class for testing inheritance."""

    class_var: ClassVar[str] = "parent_class_var"

    def parent_method(self) -> str:
        """Parent method."""
        return "parent_method"

    @staticmethod
    def parent_static_method() -> str:
        """Parent static method."""
        return "parent_static_method"

    @classmethod
    def parent_class_method(cls) -> str:
        """Parent class method."""
        return "parent_class_method"

    @property
    def parent_property(self) -> str:
        """Parent property."""
        return "parent_property"


class ChildTestClass(ParentClass):
    """Test class."""

    class_var: ClassVar[str] = "test_class_var"

    def instance_method(self) -> str:
        """Instance method."""
        return "instance_method"

    @staticmethod
    def static_method() -> str:
        """Return a static method value."""
        return "static_method"

    @classmethod
    def class_method(cls) -> str:
        """Class method."""
        return "class_method"

    @property
    def prop(self) -> str:
        """Property method."""
        return "property"

    def _private_method(self) -> str:
        """Private method."""
        return "private_method"


class GrandchildTestClass(ChildTestClass):
    """Grandchild class for testing multiple levels of inheritance."""

    def grandchild_method(self) -> str:
        """Grandchild method."""
        return "grandchild_method"


class DiamondBase:
    """Base of a diamond hierarchy, reachable through two separate branches."""


class DiamondLeft(DiamondBase):
    """Left branch of the diamond, a sibling of `DiamondRight`."""


class DiamondRight(DiamondBase):
    """Right branch of the diamond, a sibling of `DiamondLeft`."""


class DiamondJoin(DiamondLeft, DiamondRight):
    """Joins both diamond branches; reachable from `DiamondBase` twice over."""


class AbstractParent(ABC):
    """Abstract parent class for testing."""

    @abstractmethod
    def abstract_method(self) -> str:
        """Abstract method that must be implemented."""


class ConcreteChild(AbstractParent):
    """Concrete implementation of AbstractParent."""

    def __init__(self) -> None:
        """Initialize ConcreteChild."""
        super().__init__()

    def abstract_method(self) -> str:
        """Implement the abstract method."""
        return "concrete_implementation"


class AnotherAbstractChild(AbstractParent):
    """Another abstract child that doesn't implement the method."""

    @abstractmethod
    def another_abstract_method(self) -> str:
        """Another abstract method."""


class Unrelated:
    """A plain class with no relation to any other class in this module."""


def test_discover_subclasses() -> None:
    """Test func."""
    # Test with ParentClass - should find TestClass as subclass
    subclasses = discover_subclasses(ParentClass)

    assert subclasses == (ChildTestClass, GrandchildTestClass)

    # Test with TestClass - should have no subclasses
    assert discover_subclasses(ChildTestClass) == (GrandchildTestClass,)

    # Test with GrandchildTestClass - should have no subclasses
    assert discover_subclasses(GrandchildTestClass) == ()

    # A class that has never been subclassed at all.
    assert discover_subclasses(Unrelated) == ()


def test_discover_subclasses_multiple_inheritance() -> None:
    """Test func."""
    # DiamondJoin is reachable from DiamondBase through both DiamondLeft and
    # DiamondRight; it must still be discovered exactly once, not duplicated
    # or missed because of the two incoming paths.
    assert discover_subclasses(DiamondBase) == (DiamondRight, DiamondJoin, DiamondLeft)
    assert discover_subclasses(DiamondLeft) == (DiamondJoin,)
    assert discover_subclasses(DiamondRight) == (DiamondJoin,)
    assert discover_subclasses(DiamondJoin) == ()


def test_filter_leaf_classes() -> None:
    """Test function."""
    # Direct parent-child: the parent is discarded.
    assert set(filter_leaf_classes([ParentClass, ChildTestClass])) == {
        ChildTestClass,
    }

    # Transitive ancestors are discarded too, not just the direct parent.
    assert set(
        filter_leaf_classes([ParentClass, ChildTestClass, GrandchildTestClass]),
    ) == {GrandchildTestClass}

    # Siblings: neither is an ancestor of the other, so both are kept.
    assert set(filter_leaf_classes([DiamondLeft, DiamondRight])) == {
        DiamondLeft,
        DiamondRight,
    }

    # Diamond inheritance: every ancestor of DiamondJoin is discarded, even
    # though DiamondBase is reachable through two different subclasses.
    assert set(
        filter_leaf_classes([DiamondBase, DiamondLeft, DiamondRight, DiamondJoin]),
    ) == {DiamondJoin}

    # A single class with no relatives in the collection is kept unchanged.
    assert set(filter_leaf_classes([Unrelated])) == {Unrelated}

    # An empty collection stays empty.
    assert set(filter_leaf_classes([])) == set()

    # Classes from unrelated hierarchies are all kept.
    assert set(filter_leaf_classes([Unrelated, GrandchildTestClass])) == {
        Unrelated,
        GrandchildTestClass,
    }


def test_filter_concrete_classes() -> None:
    """Test function."""
    assert set(
        filter_concrete_classes([AbstractParent, ConcreteChild, AnotherAbstractChild]),
    ) == {ConcreteChild}

    # An ordinary, non-ABC class is never considered abstract.
    assert set(filter_concrete_classes([Unrelated])) == {Unrelated}

    # An empty collection stays empty.
    assert set(filter_concrete_classes([])) == set()


def test_generate_class() -> None:
    """Test function."""

    # Bases are local and used only in this test: `generate_class` creates
    # real classes that outlive the test until Python's cyclic garbage
    # collector reclaims them (a class holds itself alive via `__mro__`), so
    # reusing a module-level fixture class here would risk it lingering as a
    # phantom subclass in another test's `discover_subclasses` assertions.
    class Base:
        """Test class."""

    generated = generate_class(name="Generated", bases=(Base,))
    assert generated.__name__ == "Generated"
    assert generated.__bases__ == (Base,)
    assert issubclass(generated, Base)

    # Attributes come from `namespace`.
    with_namespace = generate_class(
        name="WithNamespace",
        bases=(Base,),
        namespace={"class_var": "namespace_value"},
    )
    assert getattr(with_namespace, "class_var") == "namespace_value"  # noqa: B009

    # Functions passed as `methods` become methods, keyed by their `__name__`.
    def instance_method(self: object) -> str:  # noqa: ARG001
        return "from_methods"

    with_methods = generate_class(
        name="WithMethods",
        bases=(Base,),
        methods=[instance_method],
    )
    assert getattr(with_methods(), "instance_method")() == "from_methods"  # noqa: B009

    # A method overrides a `namespace` entry of the same name.
    def overriding_method(self: object) -> str:  # noqa: ARG001
        return "overridden"

    overridden = generate_class(
        name="Overridden",
        bases=(Base,),
        namespace={"overriding_method": "not_a_method"},
        methods=[overriding_method],
    )
    assert getattr(overridden(), "overriding_method")() == "overridden"  # noqa: B009

    # `__module__` is inferred from the calling context, not from `bases`
    # or the caller of `generate_class`.
    assert generated.__module__ != __name__

    # Passing "__module__" in `namespace` sets it explicitly.
    with_module = generate_class(
        name="WithModule",
        bases=(Base,),
        namespace={"__module__": __name__},
    )
    assert with_module.__module__ == __name__

    # Bases whose own orderings are mutually inconsistent cannot be
    # combined into a single method resolution order.
    class DiamondBase:
        """Test class."""

    class DiamondLeft(DiamondBase):
        """Test class."""

    class DiamondRight(DiamondBase):
        """Test class."""

    class DiamondJoin(DiamondLeft, DiamondRight):
        """Test class."""

    with pytest.raises(TypeError):
        generate_class(name="Impossible", bases=(DiamondRight, DiamondJoin))
