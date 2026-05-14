from fastapi import APIRouter, Depends, HTTPException

from database.src.database import Database


router = APIRouter(tags=["devices"])

db_instance = Database()


@router.get("/devices")
def get_devices(db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            SELECT device_id, status, ip_address
            FROM devices
            ORDER BY device_id;
        """)

        rows = curr.fetchall()

        devices = [
            {
                "device_id": row[0],
                "status": row[1],
                "ip_address": row[2],
            }
            for row in rows
        ]

        return {"devices": devices}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))