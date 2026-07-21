"""Tests module."""

import importlib.metadata

from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pytest_mock import MockerFixture

from pyrig_runtime.core.dependencies.distribution import (
    distribution_header,
    distribution_header_value_pattern,
    distribution_metadata,
    distribution_name,
    distribution_requirement_as_module_name,
    distribution_requirements,
    distribution_summary,
)


def test_distribution_requirement_as_module_name() -> None:
    """Test function."""
    req = "some-package>=1.0.0"
    name = distribution_requirement_as_module_name(req)
    assert name == "some_package"

    req = "another-package==2.0.0"
    name = distribution_requirement_as_module_name(req)
    assert name == "another_package"

    req = "package-without-version"
    name = distribution_requirement_as_module_name(req)
    assert name == "package_without_version"

    req = "complex-package-name[extra1,extra2]>=0.1.0"
    name = distribution_requirement_as_module_name(req)
    assert name == "complex_package_name"

    req = "simplepackage"
    name = distribution_requirement_as_module_name(req)
    assert name == "simplepackage"

    req = "another_package"
    name = distribution_requirement_as_module_name(req)
    assert name == "another_package"

    req = "package.with.dots>=1.0.0"
    name = distribution_requirement_as_module_name(req)
    assert name == "package.with.dots"


def test_distribution_summary() -> None:
    """Test function."""
    metadata = distribution_metadata(
        importlib.metadata.distribution("pyrig-runtime"),
    )
    assert metadata is not None
    assert distribution_summary(metadata) == PyprojectConfigFile().project_description()
    header = distribution_header(metadata)
    assert distribution_summary(header) == PyprojectConfigFile().project_description()


def test_distribution_header_value_pattern() -> None:
    """Test function."""
    name_pattern = distribution_header_value_pattern("Name")
    requires_dist_pattern = distribution_header_value_pattern("Requires-Dist")

    for dist in importlib.metadata.distributions():
        text = dist.read_text("METADATA")
        assert text is not None

        header, _, _ = text.partition("\n\n")

        assert name_pattern.findall(header) == [dist.metadata["Name"]] == [dist.name]
        assert (
            requires_dist_pattern.findall(header)
            == (dist.metadata.get_all("Requires-Dist") or [])
            == (dist.requires or [])
        )


def test_distribution_header() -> None:
    """Test function."""
    for dist in importlib.metadata.distributions():
        text = dist.read_text("METADATA")
        assert text is not None
        assert distribution_header(text) == text.partition("\n\n")[0]


def test_distribution_name() -> None:
    """Test function."""
    metadata = "Metadata-Version: 2.1\nName: some-package\nVersion: 1.0\n"
    assert distribution_name(metadata) == "some-package"

    for dist in importlib.metadata.distributions():
        metadata = distribution_metadata(dist)
        assert metadata is not None
        header = distribution_header(metadata)
        assert header is not None
        assert distribution_name(header) == dist.name
        assert distribution_name(metadata) == dist.name


def test_distribution_requirements() -> None:
    """Test function."""
    metadata = (
        "Metadata-Version: 2.1\n"
        "Name: some-package\n"
        "Requires-Dist: requests>=2.0\n"
        "Requires-Dist: typer\n"
    )
    assert distribution_requirements(metadata) == ["requests>=2.0", "typer"]

    metadata_no_deps = "Metadata-Version: 2.1\nName: some-package\n"
    assert distribution_requirements(metadata_no_deps) == []

    for dist in importlib.metadata.distributions():
        metadata = distribution_metadata(dist)
        assert metadata is not None
        header = distribution_header(metadata)
        assert header is not None
        requires = dist.requires
        if requires is None:
            assert distribution_requirements(header) == []
            assert distribution_requirements(metadata) == []
            continue
        assert distribution_requirements(header) == requires
        assert distribution_requirements(metadata) == requires


def test_distribution_metadata(mocker: MockerFixture) -> None:
    """Test function."""
    for dist in importlib.metadata.distributions():
        assert distribution_metadata(dist) == dist.read_text("METADATA")

    dist = importlib.metadata.distribution("pyrig-runtime")
    assert distribution_metadata(dist) == dist.read_text("METADATA")

    mocker.patch.object(dist, "read_text", return_value=None)
    assert distribution_metadata(dist) is None
