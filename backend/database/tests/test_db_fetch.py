from unittest.mock import MagicMock
from psycopg2.sql import Composed

from database.src.db_fetch import fetch_table, fetch_table_where


def test_fetch_table():
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ("id",),
        ("name",),
    ]
    mock_cursor.fetchall.return_value = [
        (1, "test"),
    ]

    result = fetch_table(mock_cursor, "users")

    mock_cursor.execute.assert_called_once()
    query = mock_cursor.execute.call_args[0][0]

    assert isinstance(query, Composed)
    assert result == [{"id": 1, "name": "test"}]


def test_fetch_table_where():
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ("id",),
        ("name",),
    ]
    mock_cursor.fetchall.return_value = [
        (1, "test"),
    ]

    result = fetch_table_where(mock_cursor, "users", {"id": 1, "name": "test"})

    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]

    assert isinstance(query, Composed)
    assert values == [1, "test"]
    assert result == [{"id": 1, "name": "test"}]