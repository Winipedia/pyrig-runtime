"""Test module."""

from abc import ABC, abstractmethod
from typing import ClassVar

from pyrig_runtime.core.introspection.classes import (
    discard_abstract_classes,
    discard_parent_classes,
    discover_subclasses,
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

    assert isinstance(subclasses, set)
    assert subclasses == {ChildTestClass, GrandchildTestClass}

    # Test with TestClass - should have no subclasses
    assert discover_subclasses(ChildTestClass) == {GrandchildTestClass}

    # Test with GrandchildTestClass - should have no subclasses
    assert discover_subclasses(GrandchildTestClass) == set()

    # A class that has never been subclassed at all.
    assert discover_subclasses(Unrelated) == set()


def test_discover_subclasses_multiple_inheritance() -> None:
    """Test func."""
    # DiamondJoin is reachable from DiamondBase through both DiamondLeft and
    # DiamondRight; it must still be discovered exactly once, not duplicated
    # or missed because of the two incoming paths.
    assert discover_subclasses(DiamondBase) == {DiamondLeft, DiamondRight, DiamondJoin}
    assert discover_subclasses(DiamondLeft) == {DiamondJoin}
    assert discover_subclasses(DiamondRight) == {DiamondJoin}
    assert discover_subclasses(DiamondJoin) == set()


def test_discard_parent_classes() -> None:
    """Test function."""
    # Direct parent-child: the parent is discarded.
    assert set(discard_parent_classes([ParentClass, ChildTestClass])) == {
        ChildTestClass,
    }

    # Transitive ancestors are discarded too, not just the direct parent.
    assert set(
        discard_parent_classes([ParentClass, ChildTestClass, GrandchildTestClass]),
    ) == {GrandchildTestClass}

    # Siblings: neither is an ancestor of the other, so both are kept.
    assert set(discard_parent_classes([DiamondLeft, DiamondRight])) == {
        DiamondLeft,
        DiamondRight,
    }

    # Diamond inheritance: every ancestor of DiamondJoin is discarded, even
    # though DiamondBase is reachable through two different subclasses.
    assert set(
        discard_parent_classes([DiamondBase, DiamondLeft, DiamondRight, DiamondJoin]),
    ) == {DiamondJoin}

    # A single class with no relatives in the collection is kept unchanged.
    assert set(discard_parent_classes([Unrelated])) == {Unrelated}

    # An empty collection stays empty.
    assert set(discard_parent_classes([])) == set()

    # Classes from unrelated hierarchies are all kept.
    assert set(discard_parent_classes([Unrelated, GrandchildTestClass])) == {
        Unrelated,
        GrandchildTestClass,
    }


def test_discard_abstract_classes() -> None:
    """Test function."""
    assert set(
        discard_abstract_classes([AbstractParent, ConcreteChild, AnotherAbstractChild]),
    ) == {ConcreteChild}

    # An ordinary, non-ABC class is never considered abstract.
    assert set(discard_abstract_classes([Unrelated])) == {Unrelated}

    # An empty collection stays empty.
    assert set(discard_abstract_classes([])) == set()
