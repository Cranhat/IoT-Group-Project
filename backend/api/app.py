from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

from api.users import router as users_router
from api.tasks import router as tasks_router
from api.devices import router as devices_router
from api.tables import router as tables_router
from api.sniffer import router as sniffer_router
from api.agent import router as agent_router
from database.src.database import Database

db = Database()
app = FastAPI()

@app.on_event("startup")
def startup():
    db.initializeTables()

@app.get("/")
def read_root():
    return {"Hello from backend"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(devices_router)
app.include_router(tables_router)
app.include_router(sniffer_router)
app.include_router(agent_router)

class LoginRequest(BaseModel):
    username: str
    passcode: str

class TaskRequest(BaseModel):
    user_id: int
    problem: str

@app.post("/login")
def login(request: LoginRequest, db=Depends(db.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            SELECT 
                users.user_id,
                users.name,
                users.privilege_type,
                passwords.password
            FROM users
            JOIN passwords
                ON users.user_id = passwords.user_id
            WHERE users.name = %s;
        """, (request.username,))

        user = curr.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or passcode"
            )

        user_id, name, privilege_type, stored_password = user

        if request.passcode != stored_password:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or passcode"
            )

        return {
            "message": "Login successful",
            "user_id": user_id,
            "name": name,
            "privilege_type": privilege_type,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))