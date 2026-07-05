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


def test_discover_subclasses() -> None:
    """Test func."""
    # Test with ParentClass - should find TestClass as subclass
    subclasses = set(discover_subclasses(ParentClass))

    expected_subclasses: set[type] = {ChildTestClass, GrandchildTestClass}

    assert subclasses == expected_subclasses

    # Test with TestClass - should have no subclasses
    subclasses = set(discover_subclasses(ChildTestClass))

    expected_subclasses: set[type] = {GrandchildTestClass}

    assert subclasses == expected_subclasses

    # Test with GrandchildTestClass - should have no subclasses
    subclasses = set(discover_subclasses(GrandchildTestClass))

    assert subclasses == set()


def test_discard_parent_classes() -> None:
    """Test function."""
    classes = tuple(discard_parent_classes([ParentClass, ChildTestClass]))
    assert ParentClass not in classes, f"Expected ParentClass not in {classes}"
    assert ChildTestClass in classes, f"Expected TestClass in {classes}"


def test_discard_abstract_classes() -> None:
    """Test function."""
    classes = tuple(
        discard_abstract_classes([AbstractParent, ConcreteChild, AnotherAbstractChild])
    )
    assert AbstractParent not in classes, f"Expected AbstractParent not in {classes}"
    assert AnotherAbstractChild not in classes, (
        f"Expected AnotherAbstractChild not in {classes}"
    )
    assert ConcreteChild in classes, f"Expected ConcreteChild in {classes}"
