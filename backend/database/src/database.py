from src.db_init import *
from src.db_fetch import *
from src.db_insert import *
from src.db_update import *
from src.objects import *
from fastapi import FastAPI, Depends, HTTPException #shows warnings but works fine
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

ALLOWED_TABLES = {"users", "passwords", "devices", "task_logs", "task_result_logs", "http_logs"}
TABLE_MODELS = {
    "user": User,
    "password": Password,
    "device": Device,
    "tast_log": Task_log,
    "task_result_log": Task_result_log,
    "HTTP_log": HTTP_log
}

class Database:
    def __init__(self, host="localhost", dbname="postgres", user="postgres", password="postgres", port=5432):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.app = FastAPI()
        self._setup_routes()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
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

        self.sendQuery(users_initialization, conn, curr)
        self.sendQuery(passwords_initialization, conn, curr)
        conn.commit()

        self.close_conn(conn, curr)

    def validate_table(table: str):
        if table not in ALLOWED_TABLES:
            raise HTTPException(status_code=400, detail="Invalid table")

    def _setup_routes(self):  
        @self.app.get("/{table}")
        def get_table(table: str, db=Depends(self.get_db)):
            self.validate_table(table)
            conn, curr = db
            data = fetch_table(table, curr)
            return {"table": table, "data": data}

        @self.app.get("/{table}/{id}")
        def get_row_by_id(table: str, id: int, db=Depends(self.get_db)):
            self.validate_table(table)
            conn, curr = db
            data = self.fetch_table_where(table, id, curr)
            if not data:
                raise HTTPException(status_code=404, detail="Not found")
            return {"table": table, "id": id, "data": data}

        @self.app.post("/{table}")
        def insert(table: str, payload: dict, db=Depends(self.get_db)):
            self.validate_table(table)
            Model = TABLE_MODELS.get(table)
            try:
                validated_data = Model(**payload)
            except Exception as e:
                raise HTTPException(status_code=422, detail=str(e))

            conn, curr = db
            try:
                insert_into_table(curr, table, validated_data)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))

            return {"message": f"{table} inserted successfully"}

        @self.app.put("/{table}/{id}")
        def update(table: str, id: int, payload: dict, db=Depends(self.get_db)):
            self.validate_table(table)
            Model = TABLE_MODELS.get(table)
            try:
                validated_data = Model(**payload)
            except Exception as e:
                raise HTTPException(status_code=422, detail=str(e))

            conn, curr = db
            try:
                update_table(curr, table, validated_data, {"id": id})
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))

            return {"message": f"{table} updated successfully"}