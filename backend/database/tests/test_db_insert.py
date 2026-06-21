import pytest
from unittest.mock import MagicMock
from psycopg2.sql import Composed
from database.src.db_insert import insert_into_table
from database.src.objects import User, Device, Packet_sniffer_log, Communication_response

@pytest.fixture
def mock_cursor():
    return MagicMock()

def test_insert_user(mock_cursor):
    user = User(user_id=1, name="test_user", privilege="admin")
    insert_into_table(mock_cursor, "users", user)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "test_user", "admin"]

def test_insert_device(mock_cursor):
    device = Device(device_id=1, status="online", ip_address="192.168.1.1")
    insert_into_table(mock_cursor, "devices", device)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "online", "192.168.1.1", None, None]

def test_insert_dict(mock_cursor):
    data = {"id": 1, "name": "test"}
    insert_into_table(mock_cursor, "any_table", data)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "test"]

def test_insert_packet_sniffer_log_strips_null_bytes(mock_cursor):
    log = Packet_sniffer_log(
        sniffer_name="server_sniffer",
        port=5000,
        log="hello\x00world",
        timestamp="2026-06-11T10:19:01",
    )
    insert_into_table(mock_cursor, "packet_sniffer_logs", log)

    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values[2] == "helloworld"

def test_insert_communication_response(mock_cursor):
    from datetime import datetime
    resp = Communication_response(
        task_id="abc12345",
        response="Calculated value: 3.1415",
        timestamp=datetime.fromisoformat("2026-06-20T12:00:00")
    )
    insert_into_table(mock_cursor, "communication_responses", resp)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == ["abc12345", "Calculated value: 3.1415", datetime.fromisoformat("2026-06-20T12:00:00")]
