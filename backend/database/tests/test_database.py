import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from database.src.database import Database
from api.app import app
from api.tables import db_instance as tables_db_instance
from api import tables


@pytest.fixture
def db_instance():
    with patch("psycopg2.connect"):
        yield Database()


@pytest.fixture
def client():
    return TestClient(app)


def test_database_init(db_instance):
    assert db_instance.host == "db"


def test_validate_table():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        Database.validate_table("invalid_table")

    assert exc.value.status_code == 400


def test_get_table_route(client):
    mock_conn = MagicMock()
    mock_curr = MagicMock()

    app.dependency_overrides[tables_db_instance.get_db] = lambda: (mock_conn, mock_curr)

    mock_curr.description = [("user_id",), ("name",), ("privilege_type",)]
    mock_curr.fetchall.return_value = [(1, "test", "admin")]

    response = client.get("/tables/users")

    assert response.status_code == 200
    assert response.json() == {
        "table": "users",
        "data": [
            {
                "user_id": 1,
                "name": "test",
                "privilege_type": "admin",
            }
        ],
    }

    app.dependency_overrides.clear()


def test_insert_route(client):
    mock_conn = MagicMock()
    mock_curr = MagicMock()

    app.dependency_overrides[tables_db_instance.get_db] = lambda: (mock_conn, mock_curr)

    payload = {
        "user_id": 1,
        "name": "test",
        "privilege_type": "admin",
    }

    with patch.dict(tables.TABLE_MODELS, {"users": MagicMock(return_value=payload)}):
        response = client.post("/tables/users", json=payload)

    assert response.status_code == 200
    assert response.json() == {"message": "users inserted successfully"}
    mock_conn.commit.assert_called_once()

    app.dependency_overrides.clear()


def test_update_route(client):
    mock_conn = MagicMock()
    mock_curr = MagicMock()

    app.dependency_overrides[tables_db_instance.get_db] = lambda: (mock_conn, mock_curr)

    payload = {
        "user_id": 1,
        "name": "updated",
        "privilege_type": "admin",
    }

    with patch.dict(tables.TABLE_MODELS, {"users": MagicMock(return_value=payload)}):
        response = client.put("/tables/users/1", json=payload)

    assert response.status_code == 200
    assert response.json() == {"message": "users updated successfully"}
    mock_conn.commit.assert_called_once()

    app.dependency_overrides.clear()