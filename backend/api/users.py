from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database

router = APIRouter(tags=["users"])

db_instance = Database()


class AdminUserCreate(BaseModel):
    name: str
    password: str
    privilege_type: str


@router.get("/users")
def get_users(db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            SELECT user_id, name, privilege_type
            FROM users
            ORDER BY user_id;
        """)

        rows = curr.fetchall()

        users = [
            {
                "user_id": row[0],
                "name": row[1],
                "privilege_type": row[2],
            }
            for row in rows
        ]

        return {"users": users}

    except Exception as e:
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


@router.delete("/delete/users/{user_id}")
def delete_user(user_id: int, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute(
            "DELETE FROM passwords WHERE user_id = %s;",
            (user_id,)
        )

        curr.execute(
            "DELETE FROM users WHERE user_id = %s RETURNING user_id;",
            (user_id,)
        )

        deleted = curr.fetchone()

        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")

        conn.commit()

        return {"message": "User deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))