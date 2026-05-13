from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database


router = APIRouter(tags=["tasks"])

db_instance = Database()


class TaskRequest(BaseModel):
    user_id: int
    problem: str


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
        curr.execute("""
            SELECT device_id
            FROM devices
            WHERE status = 'online'
            ORDER BY device_id
            LIMIT 1;
        """)

        device = curr.fetchone()

        if not device:
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