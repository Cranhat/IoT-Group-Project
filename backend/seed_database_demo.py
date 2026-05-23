import psycopg2
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def default_db_host():
    if Path("/.dockerenv").exists():
        return "db"
    return "localhost"

conn = psycopg2.connect(
    host = os.getenv("DB_HOST", default_db_host()),
    dbname = os.getenv("POSTGRES_DB"),
    user = os.getenv("POSTGRES_USER"),
    password = os.getenv("POSTGRES_PASSWORD"),
    port = int(os.getenv("HOST_PORT_DB", 5432))
)

curr = conn.cursor()


curr.execute("""
INSERT INTO users (name, privilege_type)
VALUES
    ('admin', 'administrator'),
    ('alice', 'user'),
    ('bob', 'user')
ON CONFLICT DO NOTHING;
""")

curr.execute("""
INSERT INTO passwords (user_id, password)
VALUES
    ('1', '1234')
ON CONFLICT DO NOTHING;
""")

curr.execute("""
INSERT INTO devices (status, ip_address)
VALUES
    ('online', '192.168.1.10'),
    ('busy', '192.168.1.11'),
    ('offline', '192.168.1.12')
ON CONFLICT DO NOTHING;
""")


curr.execute("""
INSERT INTO task_logs (
    user_id,
    device_id,
    problem,
    status
)
VALUES
    (1, 1, '2 + 2', 'completed'),
    (2, 2, '10 * 5', 'running'),
    (3, 1, '100 / 4', 'pending');
""")

curr.execute("""
INSERT INTO task_result_logs (
    task_id,
    device_id,
    result,
    success,
    error_message
)
VALUES
    (1, 1, '4', TRUE, NULL);
""")

conn.commit()

print("Database seeded successfully")

curr.close()
conn.close()
