"""Tests for the detector module."""

from pathlib import Path
from typing import Callable, List

import pytest

from bluebeacon.detector import find_server_config


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


class TestFindServerConfig:
    """Tests for the find_server_config function."""

    @pytest.mark.parametrize(
        "scenario, file_path",
        [
            (
                "file_exists",
                "test_config.properties",
            ),
            (
                "dir_with_server_properties",
                "server.properties",
            ),
            (
                "dir_with_config_yml",
                "config.yml",
            ),
            (
                "dir_with_velocity_toml",
                "velocity.toml",
            ),
        ],
    )
    def test_find_server_config_success(
        self,
        temp_dir: Path,
        scenario: str,
        file_path: str,
    ) -> None:
        """Test find_server_config when it should succeed."""
        # Create the test file
        config_file = temp_dir / file_path
        config_file.touch()

        # For the file_exists scenario, we pass the file path directly
        if scenario == "file_exists":
            path_arg = config_file
        else:
            path_arg = temp_dir

        # Test the function
        result = find_server_config(path_arg)

        # Verify the result
        assert result == config_file

    @pytest.mark.parametrize(
        "scenario, path_arg",
        [
            (
                "file_not_exists",
                lambda temp_dir: temp_dir / "nonexistent_config.properties",
            ),
            (
                "dir_no_config_files",
                lambda temp_dir: temp_dir,
            ),
        ],
    )
    def test_find_server_config_failure(
        self,
        temp_dir: Path,
        scenario: str,
        path_arg: Callable,
    ) -> None:
        """Test find_server_config when it should fail."""
        # Create any files needed for the test
        # Get the path argument
        path = path_arg(temp_dir)

        # Test the function and verify it raises the expected exception
        with pytest.raises(FileNotFoundError) as excinfo:
            find_server_config(path)

        # Verify the error message
        assert str(path) in str(excinfo.value)

    def test_find_server_config_dir_with_multiple_config_files(
        self, temp_dir: Path
    ) -> None:
        """Test find_server_config when path is a directory with multiple config files."""
        # Create multiple config files
        config_files = ["server.properties", "config.yml", "velocity.toml"]
        for file_name in config_files:
            (temp_dir / file_name).touch()

        # Test the function - should prefer server.properties
        result = find_server_config(temp_dir)

        # Verify the result
        assert result == temp_dir / "server.properties"
