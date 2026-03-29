from src.database import *
from src.db_init import * 
from src.db_insert import *
import uvicorn

db = Database()
db.initializeTables()
app = db.app

def main():
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)