from backend.database.src.database import *
from backend.database.src.db_init import * 
from backend.database.src.db_insert import *
import uvicorn
import os

# db = Database(
#     host=os.getenv("DB_HOST", "db"),
#     dbname=os.getenv("POSTGRES_DB", "postgres"),
#     user=os.getenv("POSTGRES_USER", "postgres"),
#     password=os.getenv("POSTGRES_PASSWORD", "postgres"),
#     port=int(os.getenv("DB_PORT", "5432")),
# )
# db.initializeTables()
# app = db.app

# def main():
#     uvicorn.run("backend.database.app:app", host="0.0.0.0", port=8000, reload=False)