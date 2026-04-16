from unittest.mock import MagicMock
import pytest
from psycopg2.sql import Composed
from backend.database.src.database import *
from backend.database.src.db_init import * 
from backend.database.src.db_insert import *
from backend.database.src.db_update import *

@pytest.fixture
def mock_db():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    return mock_conn, mock_cursor


def test_insert_user(mock_db):
    conn, cursor = mock_db

    user = User(user_id=1, name="user1", privilege="admin")
    insert_into_table(cursor, "users", user)

    assert cursor.execute.call_count == 1


    query_used = cursor.execute.call_args[0][0]
    values_used = cursor.execute.call_args[0][1] 

    assert isinstance(query_used, Composed)
    assert values_used == [1, "user1", "admin"]


def test_update_user(mock_db):
    conn, cursor = mock_db
    update_table(cursor, "users", {"privilege": "superadmin"}, {"id": 1})
    assert cursor.execute.call_count == 1
    query_used = cursor.execute.call_args[0][0]
    values_used = cursor.execute.call_args[0][1]
    assert isinstance(query_used, Composed)
    assert values_used == ["superadmin", 1]