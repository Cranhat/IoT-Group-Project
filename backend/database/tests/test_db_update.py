import pytest
from unittest.mock import MagicMock
from psycopg2.sql import Composed
from database.src.db_update import update_table
from database.src.objects import User

@pytest.fixture
def mock_cursor():
    return MagicMock()

def test_update_user(mock_cursor):
    update_table(mock_cursor, "users", {"privilege": "superadmin"}, {"id": 1})
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == ["superadmin", 1]

def test_update_with_model(mock_cursor):
    user = User(user_id=1, name="updated_name", privilege="user")
    update_table(mock_cursor, "users", user, {"user_id": 1})
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "updated_name", "user", 1]

def test_update_multiple_where(mock_cursor):
    update_table(mock_cursor, "devices", {"status": "offline"}, {"name": "thermometer", "status": "unknown"})
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == ["offline", "thermometer", "unknown"]
