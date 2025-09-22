"""Tests for the ping module."""

import ipaddress
from unittest.mock import MagicMock, patch

import pytest

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
                # Call the function (Java only)
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "java")

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
                result = ping_server(
                    ipaddress.IPv4Address("127.0.0.1"), 25565, "bedrock"
                )

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
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "both")

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
                result = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "both")

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
                result = ping_server(ipv6_address, 25565, "java")

        # Verify the result and that JavaServer was called with bracketed IPv6 address
        assert result is True
        mock_java_class.assert_called_once_with("[::1]", 25565, 0.25)

    def test_ping_server_invalid_server_type(self) -> None:
        """Test ping_server with an invalid server type."""

        with pytest.raises(ValueError, match="Invalid server type"):
            ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "invalid_type")

    def test_ping_server_wait_loop_succeeds_after_notify(self) -> None:
        """Ensure the cond.wait() loop is actually entered and exits on success notify.

        We block the worker's status() until we release an event, so the main
        thread must enter the waiting loop. Then we release and expect success.
        """
        import threading

        started = threading.Event()
        release = threading.Event()

        class FakeJavaServer:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                pass

            def status(self) -> object:
                # Signal we've started and are about to block, so the caller enters cond.wait()
                started.set()
                # Block until the test allows us to continue
                release.wait(timeout=1)
                return object()

        # Run ping_server in a separate thread so we can assert it's waiting
        result_container: list[bool] = []

        def run_ping() -> None:
            res = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "java")
            result_container.append(res)

        with patch("bluebeacon.ping.JavaServer", new=FakeJavaServer):
            t = threading.Thread(target=run_ping)
            t.start()

            # Wait until the worker has started and is blocking inside status()
            assert started.wait(timeout=1), "Worker did not start in time"
            # At this point, ping thread should be waiting inside cond.wait()
            assert t.is_alive(), "Ping thread should be waiting in cond.wait()"

            # Now allow the worker to finish successfully
            release.set()
            t.join(timeout=1)
            assert not t.is_alive(), "Ping thread did not finish after release"

        assert result_container == [True]

    def test_ping_server_wait_loop_exits_after_both_finish_without_success(
        self,
    ) -> None:
        """Ensure the cond.wait() loop exits when both threads finish without success.

        We block both workers, then let them raise TimeoutError, expecting False.
        """
        import threading

        started_java = threading.Event()
        started_bedrock = threading.Event()
        release = threading.Event()

        class FakeJavaServer:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                pass

            def status(self) -> None:
                started_java.set()
                release.wait(timeout=1)
                raise TimeoutError("Java timeout")

        class FakeBedrockServer:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                pass

            def status(self) -> None:
                started_bedrock.set()
                release.wait(timeout=1)
                raise TimeoutError("Bedrock timeout")

        result_container: list[bool] = []

        def run_ping() -> None:
            res = ping_server(ipaddress.IPv4Address("127.0.0.1"), 25565, "both")
            result_container.append(res)

        with (
            patch("bluebeacon.ping.JavaServer", new=FakeJavaServer),
            patch("bluebeacon.ping.BedrockServer", new=FakeBedrockServer),
        ):
            t = threading.Thread(target=run_ping)
            t.start()

            # Wait for both workers to start and block
            assert started_java.wait(timeout=1), "Java worker did not start in time"
            assert started_bedrock.wait(
                timeout=1
            ), "Bedrock worker did not start in time"
            assert t.is_alive(), "Ping thread should be waiting in cond.wait()"

            # Let both workers finish (with failures)
            release.set()
            t.join(timeout=1)
            assert not t.is_alive(), "Ping thread did not finish after release"

        assert result_container == [False]
