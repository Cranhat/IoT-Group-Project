from database.src.db_init import *
from database.src.db_fetch import *
from database.src.db_insert import *
from database.src.db_update import *
from database.src.objects import *
from fastapi import HTTPException #shows warnings but works fine
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

ALLOWED_TABLES = {"users", "passwords", "devices", "task_logs", "task_result_logs", "http_logs", "packet_sniffer_logs"}
TABLE_MODELS = {
    "users": User,
    "passwords": Password,
    "devices": Device,
    "task_logs": Task_log,
    "task_result_logs": Task_result_log,
    "http_logs": HTTP_log,
    "packet_sniffer_logs": Packet_sniffer_log
}

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "db")
        self.dbname = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.port = int(os.getenv("HOST_PORT_DB", 5432))
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if(exc_type or exc_value or exc_traceback):
            print(f"exc_type: {exc_type}, exc_value: {exc_value}, exc_traceback: {exc_traceback}")
    
    def __str__(self):
        return f"host: {self.host}, dbname: {self.dbname}, user: {self.user}, password: {self.password}, port: {self.port}"
    
    def get_conn(self):
        return psycopg2.connect(host=self.host, dbname=self.dbname, user=self.user, password=self.password, port=self.port)
    
    def sendQuery(self, query, conn, curr):
        curr.execute(query)

    def close_conn(self, conn, curr):
        curr.close()
        conn.close()

    def get_db(self):
        conn = self.get_conn()
        curr = conn.cursor()
        try:
            yield conn, curr
        finally:
            self.close_conn(conn, curr)
    
    def initializeTables(self):
        conn = self.get_conn()
        curr = conn.cursor()

        try:
            self.sendQuery(users_initialization, conn, curr)
            self.sendQuery(passwords_initialization, conn, curr)
            self.sendQuery(devices_initialization, conn, curr)
            self.sendQuery(task_logs_initialization, conn, curr)
            self.sendQuery(task_result_logs_initialization, conn, curr)
            self.sendQuery(http_logs_initialization, conn, curr)
            self.sendQuery(packet_sniffer_logs_initialization, conn, curr)

            curr.execute("SELECT COUNT(*) FROM users")
            user_count = curr.fetchone()[0]

            if user_count == 0:
                curr.execute("""
                    INSERT INTO users (name, privilege_type)
                    VALUES ('admin', 'administrator')
                    RETURNING user_id
                """)

                admin_id = curr.fetchone()[0]

                curr.execute("""
                    INSERT INTO passwords (user_id, password)
                    VALUES (%s, %s)
                """, (admin_id, "1234"))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.close_conn(conn, curr)

    @staticmethod
    def validate_table(table: str):
        if table not in ALLOWED_TABLES:
            raise HTTPException(status_code=400, detail="Invalid table")
