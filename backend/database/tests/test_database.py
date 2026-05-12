import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.database.src.database import Database

@pytest.fixture
def db_instance():
    # Patch connect to avoid actual DB connection
    with patch("psycopg2.connect") as mock_connect:
        db = Database()
        yield db

@pytest.fixture
def client(db_instance):
    return TestClient(db_instance.app)

def test_database_init(db_instance):
    assert db_instance.host == "localhost"
    assert db_instance.dbname == "postgres"
    assert db_instance.app is not None

def test_validate_table(db_instance):
    from fastapi import HTTPException
    # validate_table is a static method but called as self.validate_table in routes
    # Actually it's defined as def validate_table(table: str): without self in database.py
    # But called as self.validate_table(table) in routes. This will fail if not fixed.
    
    with pytest.raises(HTTPException) as exc:
        Database.validate_table("invalid_table")
    assert exc.value.status_code == 400

def test_get_table_route(client, db_instance):
    mock_conn = MagicMock()
    mock_curr = MagicMock()
    db_instance.app.dependency_overrides[db_instance.get_db] = lambda: (mock_conn, mock_curr)
    
    with patch("backend.database.src.database.fetch_table") as mock_fetch:
        mock_fetch.return_value = [{"id": 1}]
        
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == {"table": "users", "data": [{"id": 1}]}
    db_instance.app.dependency_overrides.clear()

def test_insert_route(client, db_instance):
    mock_conn = MagicMock()
    mock_curr = MagicMock()
    db_instance.app.dependency_overrides[db_instance.get_db] = lambda: (mock_conn, mock_curr)
    
    with patch("backend.database.src.database.insert_into_table") as mock_insert:
        payload = {"user_id": 1, "name": "test", "privilege": "admin"}
        response = client.post("/users", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "users inserted successfully"}
        mock_conn.commit.assert_called_once()
    db_instance.app.dependency_overrides.clear()

def test_update_route(client, db_instance):
    mock_conn = MagicMock()
    mock_curr = MagicMock()
    db_instance.app.dependency_overrides[db_instance.get_db] = lambda: (mock_conn, mock_curr)
    
    with patch("backend.database.src.database.update_table") as mock_update:
        payload = {"user_id": 1, "name": "updated", "privilege": "admin"}
        response = client.put("/users/1", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "users updated successfully"}
        mock_conn.commit.assert_called_once()
    db_instance.app.dependency_overrides.clear()