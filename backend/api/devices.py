from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database


router = APIRouter(tags=["devices"])

db_instance = Database()

class Device(BaseModel):
    status: str
    ip_address: str


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
    

@router.post("/add/devices")
def add_device(request: Device, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            INSERT INTO devices (status, ip_address)
            VALUES (%s, %s)
            RETURNING device_id;
        """, (request.status, request.ip_address))

        device_id = curr.fetchone()[0]

        conn.commit()

        return {
            "message": "Device added successfully",
            "device_id": device_id,
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/devices/{device_id}")
def update_device(device_id: int, request: Device, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            UPDATE devices
            SET status = %s,
                ip_address = %s
            WHERE device_id = %s
            RETURNING device_id;
        """, (request.status, request.ip_address, device_id))

        updated = curr.fetchone()

        if not updated:
            raise HTTPException(status_code=404, detail="Device not found")

        conn.commit()

        return {
            "message": "Device updated successfully",
            "device_id": device_id,
        }

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/delete/devices/{device_id}")
def delete_device(device_id: int, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute(
            "DELETE FROM devices WHERE device_id = %s RETURNING device_id;",
            (device_id,)
        )

        deleted = curr.fetchone()

        if not deleted:
            raise HTTPException(status_code=404, detail="Device not found")

        conn.commit()
        return {"message": "Device deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))