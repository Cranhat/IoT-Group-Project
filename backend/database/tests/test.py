from unittest.mock import MagicMock
import pytest
from backend.database.src.database import *
from backend.database.src.db_init import * 
from backend.database.src.db_create import *
from backend.database.src.db_update import *

@pytest.fixture
def mock_db():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    return mock_conn, mock_cursor


def test_insert_user(mock_db):
    conn, cursor = mock_db

    user = User(id=1, name="Bajojajo", privilege="admin")
    insert_into_table(cursor, "users", user)

    # Check that cursor.execute was called once
    assert cursor.execute.call_count == 1

    # Check the query and values
    query_used = cursor.execute.call_args[0][0].as_string(cursor)  # get SQL as string
    values_used = cursor.execute.call_args[0][1]  # values passed

    assert "INSERT INTO" in query_used
    assert values_used == [1, "Bajojajo", "admin"]


def test_update_user(mock_db):
    conn, cursor = mock_db
    update_table(cursor, "users", {"privilege": "bambik"}, {"id": 1})
    assert cursor.execute.call_count == 1
    query_used = cursor.execute.call_args[0][0].as_string(cursor)
    values_used = cursor.execute.call_args[0][1]
    assert "UPDATE" in query_used
    assert values_used == ["bambik", 1]