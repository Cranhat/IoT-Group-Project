from backend.database.src.db_init import *
from backend.database.src.db_read import *
from backend.database.src.db_create import *
from backend.database.src.objects import *
from fastapi import FastAPI
from fastapi import Depends
import psycopg2


class Database:
    def __init__(self, host="localhost", dbname="postgres", user="postgres", password="postgres", port=5432):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.app = FastAPI()
        self._setup_routes()
        
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

    def commit(self, conn, curr):
        conn.commit()

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

    def fetchData(self, query, conn, curr):
        curr.execute(query)
        data = curr.fetchall()
        return data
 
    def _setup_routes(self):
        @self.app.get("/")
        def read_root():
            return {"message": "Welcome!"}
        

        # --- Users --- 
        @self.app.get("/users") # get users
        def get_users(db = Depends(self.get_db)):
            conn, curr = db
            query = create_fetch().format(*('*', 'users'))
            data = self.fetchData(query, conn, curr)
            return {"data": data} 
        
        @self.app.get("/users/{id}") # get user
        def get_user(id: int, db = Depends(self.get_db)):
            conn, curr = db
            query = create_fetch_where().format(*('*', 'users', f'id = {id}'))
            data = self.fetchData(query, conn, curr)
            return {"id": id, "data": data} 
        
        @self.app.post("/users/") # post user
        async def create_user(user: User, db = Depends(self.get_db)):
            conn, curr = db
            insert_into_table(curr, "users", user)
            self.commit(conn, curr)
            return {"message": "User added"}
        