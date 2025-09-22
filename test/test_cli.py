"""Tests for the CLI module."""

import ipaddress
from pathlib import Path

from click.testing import CliRunner
from pytest_mock import MockerFixture, MockType

from bluebeacon import cli


class TestCli:
    """Tests for the main CLI function."""

    def test_00_version_long_flag(self) -> None:
        """--version should print version and exit with code 0 (first)."""
        runner = CliRunner()
        result = runner.invoke(cli.main, ["--version"])
        assert result.exit_code == 0
        # Expect output like: "BlueBeacon v0.1.1\n"
        assert result.output.startswith("BlueBeacon v")
        assert result.output.endswith("\n")
        # Ensure there is something after the 'v'
        assert len(result.output.strip()) > len("BlueBeacon v")

    def test_01_version_short_flag(self) -> None:
        """-V should print version and exit with code 0 (first)."""
        runner = CliRunner()
        result = runner.invoke(cli.main, ["-V"])
        assert result.exit_code == 0
        assert result.output.startswith("BlueBeacon v")
        assert result.output.endswith("\n")
        assert len(result.output.strip()) > len("BlueBeacon v")

    def test_main_success_no_args(self, mocker: MockerFixture) -> None:
        """Test the main function with no arguments when config is found."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Mock the ping.ping_server function to return True
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = True

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

        # Mock the ping.ping_server function to return True
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = True

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

        # Mock the ping.ping_server function to return True
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = True

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

    def test_main_server_reachable(self, mocker: MockerFixture) -> None:
        """Test the main function when server is unreachable."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Mock the ping.ping_server function to return False (server unreachable)
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = True

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert result.exit_code == 0
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "both"
        )

    def test_main_server_unreachable(self, mocker: MockerFixture) -> None:
        """Test the main function when server is unreachable."""
        # Mock the detector.find_server_config function to return a Path
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")

        # Mock the detector.parse_server_config function to return address and port
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Mock the ping.ping_server function to return False (server unreachable)
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = False

        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(cli.main)

        # Verify the result and the mocks
        assert result.exit_code == 1
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "both"
        )


class TestCliServerTypeFlags:
    @staticmethod
    def _common_mocks(mocker: MockerFixture) -> MockType:
        mock_find_config = mocker.patch("bluebeacon.detector.find_server_config")
        mock_find_config.return_value = Path("/mock/path/server.properties")
        mock_parse_config = mocker.patch("bluebeacon.detector.parse_server_config")
        mock_parse_config.return_value = (ipaddress.IPv4Address("127.0.0.1"), 25565)
        mock_ping = mocker.patch("bluebeacon.ping.ping_server")
        mock_ping.return_value = True

        return mock_ping

    def test_flag_java(self, mocker: MockerFixture) -> None:
        mock_ping = self._common_mocks(mocker)
        runner = CliRunner()
        result = runner.invoke(cli.main, ["--java"])
        assert result.exit_code == 0
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "java"
        )

    def test_flag_bedrock(self, mocker: MockerFixture) -> None:
        mock_ping = self._common_mocks(mocker)
        runner = CliRunner()
        result = runner.invoke(cli.main, ["--bedrock"])
        assert result.exit_code == 0
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "bedrock"
        )

    def test_flag_both(self, mocker: MockerFixture) -> None:
        mock_ping = self._common_mocks(mocker)
        runner = CliRunner()
        result = runner.invoke(cli.main, ["--both"])
        assert result.exit_code == 0
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "both"
        )

    def test_flag_none(self, mocker: MockerFixture) -> None:
        mock_ping = self._common_mocks(mocker)
        runner = CliRunner()
        result = runner.invoke(cli.main, [])
        assert result.exit_code == 0
        mock_ping.assert_called_once_with(
            ipaddress.IPv4Address("127.0.0.1"), 25565, "both"
        )
