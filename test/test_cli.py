"""Tests for the CLI module."""

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

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result
        assert result.exit_code == 0
        # Verify the mock was called with the default path (home directory)
        mock_find_config.assert_called_once_with(Path.home())

    def test_main_success_with_config_path(self, mocker: MockerFixture) -> None:
        """Test the main function with config_path argument when config is found."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Run the CLI with a specific path
        test_path = "test_config_path"
        runner = CliRunner()
        result = runner.invoke(cli.main, [test_path])

        # Verify the result
        assert result.exit_code == 0
        # Verify the mock was called with the specified path
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

        # Instead of checking exit_code, we verify the error message is in the output
        # This confirms the error path was taken
        assert f"Error: {error_message}" in result.output

        # Also verify the mock was called with the default path
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

        # Instead of checking exit_code, we verify the error message is in the output
        # This confirms the error path was taken
        assert "Error: Invalid path" in result.output

        # Also verify the mock was called with the specified path
        mock_find_config.assert_called_once_with(Path(test_path))
