import pytest
import json
import os
import sys
from pathlib import Path
import logging
from unittest.mock import MagicMock, patch, call

os.environ.setdefault("MONITORED_PORT", "8080")
os.environ.setdefault("SNIFFER_TIMEOUT", "10")

PACKET_SNIFFER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKET_SNIFFER_DIR))


from main import signal_handler, check_permissions, process_packet, save_packet_log, sanitize_log_text, main


# --- signal_handler tests ---

def test_signal_handler_exits(caplog):
    """signal_handler logs a message and calls sys.exit(0)."""
    with pytest.raises(SystemExit) as exc_info:
        signal_handler(2, None)
    assert exc_info.value.code == 0


# --- check_permissions tests ---

@patch("main.os.geteuid", create=True, return_value=0)
def test_check_permissions_as_root(mock_geteuid):
    assert check_permissions() is True


@patch("main.os.geteuid", create=True, return_value=1000)
def test_check_permissions_not_root(mock_geteuid, caplog):
    with caplog.at_level(logging.WARNING):
        result = check_permissions()
    assert result is False
    assert "Root privileges missing" in caplog.text


# --- process_packet tests ---

def _make_packet(ip_src, ip_dst, sport, dport, raw_data=None):
    packet = MagicMock()

    ip_layer = MagicMock()
    ip_layer.src = ip_src
    ip_layer.dst = ip_dst

    tcp_layer = MagicMock()
    tcp_layer.sport = sport
    tcp_layer.dport = dport

    raw_layer = MagicMock()
    if raw_data is not None:
        raw_layer.load = raw_data

    layer_map = {}

    from scapy.all import IP, TCP, Raw
    layer_map[IP] = ip_layer
    layer_map[TCP] = tcp_layer
    layer_map[Raw] = raw_layer

    packet.__getitem__ = MagicMock(side_effect=lambda key: layer_map[key])

    if raw_data is not None:
        packet.haslayer.return_value = True
    else:
        def haslayer_side_effect(layer):
            return layer in (IP, TCP)
        packet.haslayer.side_effect = haslayer_side_effect

    return packet


def test_process_packet_captures_matching_port(caplog):
    """Logs captured packet info when sport matches MONITORED_PORT."""
    packet = _make_packet("192.168.1.10", "192.168.1.20", 8080, 443,
                          raw_data=b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n")
    with caplog.at_level(logging.INFO):
        process_packet(packet)
    assert "CAPTURED" in caplog.text
    assert "192.168.1.10" in caplog.text


def test_process_packet_captures_matching_dport(caplog):
    """Logs captured packet info when dport matches MONITORED_PORT."""
    packet = _make_packet("10.0.0.1", "10.0.0.2", 12345, 8080,
                          raw_data=b"HTTP/1.1 200 OK\r\n\r\n")
    with caplog.at_level(logging.INFO):
        process_packet(packet)
    assert "CAPTURED" in caplog.text
    assert "10.0.0.1" in caplog.text


def test_process_packet_ignores_non_matching_port(caplog):
    """Does not log when neither sport nor dport matches MONITORED_PORT."""
    packet = _make_packet("10.0.0.1", "10.0.0.2", 9999, 9999,
                          raw_data=b"some data")
    with caplog.at_level(logging.INFO):
        process_packet(packet)
    assert "CAPTURED" not in caplog.text


def test_process_packet_no_tcp_layer(caplog):
    """Does nothing when packet has no TCP layer."""
    packet = MagicMock()
    packet.haslayer.return_value = False

    with caplog.at_level(logging.INFO):
        process_packet(packet)
    assert "CAPTURED" not in caplog.text


def test_process_packet_no_raw_layer(caplog):
    """Does not log payload when packet has IP+TCP but no Raw layer."""
    packet = _make_packet("10.0.0.1", "10.0.0.2", 8080, 443, raw_data=None)
    with caplog.at_level(logging.INFO):
        process_packet(packet)
    assert "CAPTURED" not in caplog.text


def test_process_packet_handles_exception(caplog):
    """Logs an error when packet processing raises an exception."""
    packet = MagicMock()
    packet.haslayer.side_effect = Exception("unexpected error")

    with caplog.at_level(logging.ERROR):
        process_packet(packet)
    assert "Packet processing error" in caplog.text


def test_save_packet_log_retries_transient_backend_refusal(caplog):
    """Retries backend writes so startup races do not drop packet logs immediately."""
    with patch("main.BACKEND_API_URL", "http://backend:8000"), \
         patch("main.BACKEND_SAVE_RETRIES", 2), \
         patch("main.BACKEND_SAVE_RETRY_DELAY", 0.1), \
         patch("main.time.sleep") as mock_sleep, \
         patch("main.urllib.request.urlopen", side_effect=[OSError("connection refused"), MagicMock()]) as mock_urlopen:
        with caplog.at_level(logging.WARNING):
            assert save_packet_log(8080, "payload") is True

    assert mock_urlopen.call_count == 2
    mock_sleep.assert_called_once_with(0.1)
    assert "Failed to save packet log" not in caplog.text


def test_save_packet_log_strips_null_bytes_before_posting():
    with patch("main.BACKEND_API_URL", "http://backend:8000"), \
         patch("main.urllib.request.urlopen") as mock_urlopen:
        assert save_packet_log(5000, "abc\x00def") is True

    request = mock_urlopen.call_args[0][0]
    payload = json.loads(request.data.decode("utf-8"))

    assert payload["log"] == "abcdef"
    assert sanitize_log_text("a\x00b") == "ab"


# --- main tests ---

@patch("main.sniff")
@patch("main.check_permissions", return_value=True)
@patch("main.time.sleep")
@patch("main.signal.signal")
def test_main_runs_sniffer(mock_signal, mock_sleep, mock_check, mock_sniff):
    main()

    assert mock_signal.call_count == 2

    mock_sleep.assert_called_once_with(2)

    mock_sniff.assert_called_once()
    call_kwargs = mock_sniff.call_args[1]
    assert "8080" in call_kwargs["filter"]
    assert call_kwargs["store"] is False


@patch("main.sniff", side_effect=PermissionError("denied"))
@patch("main.check_permissions", return_value=False)
@patch("main.time.sleep")
@patch("main.signal.signal")
def test_main_permission_error_exits(mock_signal, mock_sleep, mock_check, mock_sniff):
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


@patch("main.sniff", side_effect=RuntimeError("network down"))
@patch("main.check_permissions", return_value=True)
@patch("main.time.sleep")
@patch("main.signal.signal")
def test_main_generic_error_exits(mock_signal, mock_sleep, mock_check, mock_sniff):
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
