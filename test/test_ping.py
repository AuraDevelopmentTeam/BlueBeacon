"""Tests for the ping module."""

import ipaddress
from unittest.mock import MagicMock, patch

from bluebeacon.ping import ping_server


class TestPingServer:
    """Tests for the ping_server function."""

    def test_ping_server_java_success(self) -> None:
        """Test ping_server when Java server responds successfully."""
        # Mock JavaServer to return a successful status
        mock_java_server = MagicMock()
        mock_java_server.status.return_value = MagicMock()  # Successful status

        # Mock BedrockServer to raise an exception (not used in this test)
        mock_bedrock_server = MagicMock()
        mock_bedrock_server.status.side_effect = TimeoutError("Timeout")

        # Patch the server classes
        with patch(
            "bluebeacon.ping.JavaServer", return_value=mock_java_server
        ) as mock_java_class:
            with patch(
                "bluebeacon.ping.BedrockServer", return_value=mock_bedrock_server
            ):
                # Call the function
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Verify the result and that JavaServer was called correctly
        assert result is True
        mock_java_class.assert_called_once_with("127.0.0.1", 25565, 0.25)
        mock_java_server.status.assert_called_once()

    def test_ping_server_bedrock_success(self) -> None:
        """Test ping_server when Bedrock server responds successfully."""
        # Mock JavaServer to raise an exception
        mock_java_server = MagicMock()
        mock_java_server.status.side_effect = TimeoutError("Timeout")

        # Mock BedrockServer to return a successful status
        mock_bedrock_server = MagicMock()
        mock_bedrock_server.status.return_value = MagicMock()  # Successful status

        # Patch the server classes
        with patch("bluebeacon.ping.JavaServer", return_value=mock_java_server):
            with patch(
                "bluebeacon.ping.BedrockServer", return_value=mock_bedrock_server
            ) as mock_bedrock_class:
                # Call the function
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Verify the result and that BedrockServer was called correctly
        assert result is True
        mock_bedrock_class.assert_called_once_with("127.0.0.1", 25565, 0.25)
        mock_bedrock_server.status.assert_called_once()

    def test_ping_server_both_fail(self) -> None:
        """Test ping_server when both Java and Bedrock servers fail to respond."""
        # Mock both server types to raise exceptions
        mock_java_server = MagicMock()
        mock_java_server.status.side_effect = TimeoutError("Java timeout")

        mock_bedrock_server = MagicMock()
        mock_bedrock_server.status.side_effect = TimeoutError("Bedrock timeout")

        # Patch the server classes
        with patch("bluebeacon.ping.JavaServer", return_value=mock_java_server):
            with patch(
                "bluebeacon.ping.BedrockServer", return_value=mock_bedrock_server
            ):
                # Call the function
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Verify the result
        assert result is False

    def test_ping_server_java_io_error(self) -> None:
        """Test ping_server when Java server raises an IOError."""
        # Mock JavaServer to raise an IOError
        mock_java_server = MagicMock()
        mock_java_server.status.side_effect = IOError("Connection refused")

        # Mock BedrockServer to raise a TimeoutError
        mock_bedrock_server = MagicMock()
        mock_bedrock_server.status.side_effect = TimeoutError("Timeout")

        # Patch the server classes
        with patch("bluebeacon.ping.JavaServer", return_value=mock_java_server):
            with patch(
                "bluebeacon.ping.BedrockServer", return_value=mock_bedrock_server
            ):
                # Call the function
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565)

        # Verify the result
        assert result is False

    def test_ping_server_ipv6_address(self) -> None:
        """Test ping_server with an IPv6 address."""
        ipv6_address = ipaddress.IPv6Address("::1")

        # Mock both server types
        mock_java_server = MagicMock()
        mock_java_server.status.return_value = MagicMock()  # Successful status

        mock_bedrock_server = MagicMock()

        # Patch the server classes
        with patch(
            "bluebeacon.ping.JavaServer", return_value=mock_java_server
        ) as mock_java_class:
            with patch(
                "bluebeacon.ping.BedrockServer", return_value=mock_bedrock_server
            ):
                # Call the function
                result = ping_server(ipv6_address, 25565)

        # Verify the result and that JavaServer was called with bracketed IPv6 address
        assert result is True
        mock_java_class.assert_called_once_with("[::1]", 25565, 0.25)
