import pytest
from unittest.mock import MagicMock
from psycopg2.sql import Composed
from backend.database.src.db_insert import insert_into_table
from backend.database.src.objects import User, Device

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
    device = Device(device_id=1, status="online", ip_adress="192.168.1.1")
    insert_into_table(mock_cursor, "devices", device)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "online", "192.168.1.1"]

def test_insert_dict(mock_cursor):
    data = {"id": 1, "name": "test"}
    insert_into_table(mock_cursor, "any_table", data)
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "test"]
