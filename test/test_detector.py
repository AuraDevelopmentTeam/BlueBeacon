"""Tests for the detector module."""

import ipaddress
from pathlib import Path
from typing import Callable
from unittest.mock import mock_open, patch

import pytest

# noinspection PyProtectedMember
# For testing purposes
from bluebeacon.detector import (
    _parse_ini_config,
    _parse_toml_config,
    _parse_yaml_config,
    find_server_config,
    parse_server_config,
)


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


class TestParseIniConfig:
    """Tests for the _parse_ini_config function."""

    def test_parse_valid_ini_config(self) -> None:
        """Test parsing a valid INI config file."""
        config_content = "server-address=192.168.1.10\nserver-port=25565"
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_ini_config(Path("server.properties"))

        assert result is not None
        ip, port = result
        assert ip == ipaddress.ip_address("192.168.1.10")
        assert port == 25565

    def test_parse_ini_missing_fields(self) -> None:
        """Test parsing an INI file with missing fields."""
        config_content = "server-name=MyServer\ndifficulty=hard"
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_ini_config(Path("server.properties"))

        assert result is None

    def test_parse_ini_invalid_format(self) -> None:
        """Test parsing an invalid INI file."""
        # Create invalid content that will cause javaproperties to raise an exception
        config_content = "server-address=192.168.1.10\\uXYZ"  # Invalid unicode escape
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_ini_config(Path("server.properties"))

        assert result is None


class TestParseYamlConfig:
    """Tests for the _parse_yaml_config function."""

    def test_parse_valid_yaml_config(self) -> None:
        """Test parsing a valid YAML config file."""
        config_content = """
        listeners:
          - host: 192.168.1.20:25566
            motd: My Minecraft Server
        """
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_yaml_config(Path("config.yml"))

        assert result is not None
        ip, port = result
        assert ip == ipaddress.ip_address("192.168.1.20")
        assert port == 25566

    def test_parse_yaml_missing_fields(self) -> None:
        """Test parsing a YAML file with missing fields."""
        config_content = """
        motd: My Minecraft Server
        max-players: 20
        """
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_yaml_config(Path("config.yml"))

        assert result is None

    def test_parse_yaml_invalid_format(self) -> None:
        """Test parsing an invalid YAML file."""
        # Create invalid YAML content
        config_content = """
        listeners:
          - host: 192.168.1.20:25566
            - invalid indentation
        """
        mock_file = mock_open(read_data=config_content)

        with patch("pathlib.Path.open", mock_file):
            result = _parse_yaml_config(Path("config.yml"))

        assert result is None


class TestParseTomlConfig:
    """Tests for the _parse_toml_config function."""

    def test_parse_valid_toml_config(self) -> None:
        """Test parsing a valid TOML config file."""
        config_content = """
        bind = "192.168.1.30:25567"
        motd = "My Velocity Server"
        """
        mock_file = mock_open(read_data=config_content.encode())

        with patch("pathlib.Path.open", mock_file):
            result = _parse_toml_config(Path("velocity.toml"))

        assert result is not None
        ip, port = result
        assert ip == ipaddress.ip_address("192.168.1.30")
        assert port == 25567

    def test_parse_toml_missing_fields(self) -> None:
        """Test parsing a TOML file with missing fields."""
        config_content = """
        motd = "My Velocity Server"
        player-limit = 100
        """
        mock_file = mock_open(read_data=config_content.encode())

        with patch("pathlib.Path.open", mock_file):
            result = _parse_toml_config(Path("velocity.toml"))

        assert result is None

    def test_parse_toml_invalid_format(self) -> None:
        """Test parsing an invalid TOML file."""
        # Create invalid TOML content
        config_content = """
        bind = "192.168.1.30:25567"
        motd = "My Velocity Server
        """  # Missing closing quote
        mock_file = mock_open(read_data=config_content.encode())

        with patch("pathlib.Path.open", mock_file):
            result = _parse_toml_config(Path("velocity.toml"))

        assert result is None


class TestParseServerConfig:
    """Tests for the parse_server_config function."""

    def test_parse_ini_config(self) -> None:
        """Test parsing a server.properties file."""
        config_file = Path("server.properties")
        expected_result = (ipaddress.ip_address("192.168.1.10"), 25565)

        with patch("bluebeacon.detector._parse_ini_config") as mock_parse:
            mock_parse.return_value = expected_result
            with patch("bluebeacon.detector._parse_yaml_config") as mock_yaml:
                mock_yaml.return_value = None
                with patch("bluebeacon.detector._parse_toml_config") as mock_toml:
                    mock_toml.return_value = None
                    result = parse_server_config(config_file)

        assert result == expected_result

    def test_parse_yaml_config(self) -> None:
        """Test parsing a config.yml file."""
        config_file = Path("config.yml")
        expected_result = (ipaddress.ip_address("192.168.1.20"), 25566)

        with patch("bluebeacon.detector._parse_ini_config") as mock_parse:
            mock_parse.return_value = None
            with patch("bluebeacon.detector._parse_yaml_config") as mock_yaml:
                mock_yaml.return_value = expected_result
                with patch("bluebeacon.detector._parse_toml_config") as mock_toml:
                    mock_toml.return_value = None
                    result = parse_server_config(config_file)

        assert result == expected_result

    def test_parse_toml_config(self) -> None:
        """Test parsing a velocity.toml file."""
        config_file = Path("velocity.toml")
        expected_result = (ipaddress.ip_address("192.168.1.30"), 25567)

        with patch("bluebeacon.detector._parse_ini_config") as mock_parse:
            mock_parse.return_value = None
            with patch("bluebeacon.detector._parse_yaml_config") as mock_yaml:
                mock_yaml.return_value = None
                with patch("bluebeacon.detector._parse_toml_config") as mock_toml:
                    mock_toml.return_value = expected_result
                    result = parse_server_config(config_file)

        assert result == expected_result

    def test_unsupported_config_format(self) -> None:
        """Test parsing an unsupported config file format."""
        config_file = Path("unknown.cfg")

        with patch("bluebeacon.detector._parse_ini_config") as mock_parse:
            mock_parse.return_value = None
            with patch("bluebeacon.detector._parse_yaml_config") as mock_yaml:
                mock_yaml.return_value = None
                with patch("bluebeacon.detector._parse_toml_config") as mock_toml:
                    mock_toml.return_value = None

                    with pytest.raises(ValueError) as excinfo:
                        parse_server_config(config_file)

        assert str(config_file) in str(excinfo.value)
