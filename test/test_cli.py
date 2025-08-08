"""Tests for the CLI module."""

import ipaddress
from pathlib import Path

from click.testing import CliRunner
from pytest_mock import MockerFixture

from bluebeacon import cli


class TestCli:
    """Tests for the main CLI function."""

    def test_main_success_no_args(self, mocker: MockerFixture) -> None:
        """Test the main function with no arguments when config is found."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert result.exit_code == 0
        mock_find_config.assert_called_once_with(Path.home())

    def test_main_success_with_config_path(self, mocker: MockerFixture) -> None:
        """Test the main function with config_path argument when config is found."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Run the CLI with a specific path
        test_path = "test_config_path"
        runner = CliRunner()
        result = runner.invoke(cli.main, [test_path])

        # Verify the result and the mocks
        assert result.exit_code == 0
        mock_find_config.assert_called_once_with(Path(test_path))

    def test_main_failure_config_not_found(self, mocker: MockerFixture) -> None:
        """Test the main function when config is not found."""
        # Mock the detector.find_server_config function to raise FileNotFoundError
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        error_message = "No valid server configuration found in /test/path"
        mock_find_config.side_effect = FileNotFoundError(error_message)

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert f"Error: {error_message}" in result.output
        assert result.exit_code == 2
        mock_find_config.assert_called_once_with(Path.home())

    def test_main_with_invalid_path(self, mocker: MockerFixture) -> None:
        """Test the main function with an invalid path."""
        # Mock the detector.find_server_config function to raise FileNotFoundError
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.side_effect = FileNotFoundError("Invalid path")

        # Run the CLI with an invalid path
        test_path = "/invalid/path"
        runner = CliRunner()
        result = runner.invoke(cli.main, [test_path])

        # Verify the result and the mocks
        assert "Error: Invalid path" in result.output
        assert result.exit_code == 2
        mock_find_config.assert_called_once_with(Path(test_path))

    def test_main_success_with_parse_config(self, mocker: MockerFixture) -> None:
        """Test the main function with successful config parsing."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert result.exit_code == 0
        mock_parse_config.assert_called_once_with(Path("/mock/path/server.properties"))

    def test_main_failure_parse_config(self, mocker: MockerFixture) -> None:
        """Test the main function when config parsing fails."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to raise ValueError
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        error_message = "Unsupported server config file format"
        mock_parse_config.side_effect = ValueError(error_message)

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert f"Error: {error_message}" in result.output
        assert result.exit_code == 2
        mock_parse_config.assert_called_once_with(Path("/mock/path/server.properties"))
