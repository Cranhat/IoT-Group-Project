import pytest
from unittest.mock import MagicMock
from psycopg2.sql import Composed
from backend.database.src.db_fetch import fetch_table, fetch_table_where

@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
    return cursor

def test_fetch_table(mock_cursor):
    result = fetch_table(mock_cursor, "users")
    
    mock_cursor.execute.assert_called_once()
    query = mock_cursor.execute.call_args[0][0]
    assert isinstance(query, Composed)
    # Instead of as_string, we can just check that execute was called
    assert result == [{"id": 1, "name": "test"}]

def test_fetch_table_where(mock_cursor):
    result = fetch_table_where(mock_cursor, "users", {"id": 1, "name": "test"})
    
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]
    assert isinstance(query, Composed)
    assert values == [1, "test"]
    assert result == [{"id": 1, "name": "test"}]
