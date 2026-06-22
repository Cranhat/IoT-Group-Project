from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database


router = APIRouter(tags=["tasks"])

db_instance = Database()


class TaskRequest(BaseModel):
    user_id: int
    problem: str
    device_id: int | None = None

class AdminUserCreate(BaseModel):
    name: str
    password: str
    privilege_type: str

@router.get("/tasks")
def get_tasks(user_id: int, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            SELECT
                tl.task_id,
                tl.user_id,
                tl.device_id,
                tl.problem,
                tl.status,
                tl.timestamp,
                trl.result,
                trl.success,
                trl.error_message
            FROM task_logs tl
            LEFT JOIN task_result_logs trl
                ON tl.task_id = trl.task_id
            WHERE tl.user_id = %s
            ORDER BY tl.timestamp DESC;
        """, (user_id,))

        rows = curr.fetchall()

        tasks = [
            {
                "task_id": row[0],
                "user_id": row[1],
                "device_id": row[2],
                "problem": row[3],
                "status": row[4],
                "timestamp": row[5],
                "result": row[6],
                "success": row[7],
                "error_message": row[8],
            }
            for row in rows
        ]

        return {"tasks": tasks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks")
def create_task(request: TaskRequest, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        if request.device_id:
            curr.execute("""
                SELECT device_id
                FROM devices
                WHERE device_id = %s
                    AND status = 'online';
            """, (request.device_id,))
        else:
            curr.execute("""
                SELECT device_id
                FROM devices
                WHERE status = 'online'
                ORDER BY device_id
                LIMIT 1;
            """)

        device = curr.fetchone()

        if not device:
            if request.device_id:
                raise HTTPException(status_code=400, detail="Selected device is not online")

            raise HTTPException(status_code=503, detail="No online devices available")

        device_id = device[0]

        curr.execute("""
            INSERT INTO task_logs (user_id, device_id, problem, status)
            VALUES (%s, %s, %s, %s)
            RETURNING task_id, timestamp;
        """, (
            request.user_id,
            device_id,
            request.problem,
            "pending",
        ))

        task_id, timestamp = curr.fetchone()

        conn.commit()

        # Forward task to socket server HTTP endpoint
        try:
            import urllib.request
            import json
            req = urllib.request.Request(
                "http://server:8080/task",
                data=json.dumps({"task_id": str(task_id), "code": request.problem}).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                pass
        except Exception as e:
            print(f"Error forwarding task to socket server: {e}")

        return {
            "message": "Task created successfully",
            "task": {
                "task_id": task_id,
                "user_id": request.user_id,
                "device_id": device_id,
                "problem": request.problem,
                "status": "pending",
                "timestamp": timestamp,
                "result": None,
                "success": False,
                "error_message": None,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

class TaskResultRequest(BaseModel):
    device_id: int
    result: str
    success: bool
    error_message: str

@router.post("/tasks/{task_id}/result")
def save_task_result(task_id: int, request: TaskResultRequest, db=Depends(db_instance.get_db)):
    conn, curr = db
    try:
        # Insert into task_result_logs
        curr.execute("""
            INSERT INTO task_result_logs (task_id, device_id, result, success, error_message)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            task_id,
            request.device_id,
            request.result,
            request.success,
            request.error_message
        ))
        
        # Update task_logs status
        status = "completed" if request.success else "failed"
        curr.execute("""
            UPDATE task_logs
            SET status = %s
            WHERE task_id = %s;
        """, (status, task_id))
        
        conn.commit()
        return {"message": "Task result saved successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add/users")
def add_user(request: AdminUserCreate, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            INSERT INTO users (name, privilege_type)
            VALUES (%s, %s)
            RETURNING user_id;
        """, (request.name, request.privilege_type))

        user_id = curr.fetchone()[0]

        curr.execute("""
            INSERT INTO passwords (user_id, password)
            VALUES (%s, %s);
        """, (user_id, request.password))

        conn.commit()

        return {
            "message": "User added successfully",
            "user_id": user_id,
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
