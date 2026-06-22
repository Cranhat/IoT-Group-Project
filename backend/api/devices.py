import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database

router = APIRouter(tags=["devices"])

db_instance = Database()
AGENT_URL = os.getenv("AGENT_URL", "http://agent:9000")


class Device(BaseModel):
    status: str
    ip_address: str
    container_name: str | None = None
    device_name: str | None = None


@router.get("/devices")
def get_devices(db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute("""
            SELECT device_id, status, ip_address, container_name, device_name
            FROM devices
            ORDER BY device_id;
        """)

        rows = curr.fetchall()

        devices = [
            {
                "device_id": row[0],
                "status": row[1],
                "ip_address": row[2],
                "container_name": row[3],
                "device_name": row[4],
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
            INSERT INTO devices (status, ip_address, container_name, device_name)
            VALUES (%s, %s, %s, %s)
            RETURNING device_id;
        """, (
            request.status,
            request.ip_address,
            request.container_name,
            request.device_name,
        ))

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
                ip_address = %s,
                container_name = %s,
                device_name = %s
            WHERE device_id = %s
            RETURNING device_id;
        """, (
            request.status,
            request.ip_address,
            request.container_name,
            request.device_name,
            device_id,
        ))

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


class StatusUpdate(BaseModel):
    status: str


@router.put("/devices/status/{ip_address}")
def update_device_status_by_ip(ip_address: str, payload: StatusUpdate, db=Depends(db_instance.get_db)):
    conn, curr = db
    try:
        curr.execute("""
            UPDATE devices
            SET status = %s
            WHERE ip_address = %s
            RETURNING device_id;
        """, (payload.status, ip_address))

        row = curr.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Device with ip_address '{ip_address}' not found")

        conn.commit()
        return {
            "message": "Device status updated successfully",
            "device_id": row[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/offline-all")
def mark_all_devices_offline(db=Depends(db_instance.get_db)):
    conn, curr = db
    try:
        curr.execute("UPDATE devices SET status = 'offline';")
        conn.commit()
        return {"message": "All devices marked offline"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/devices/{device_id}")
def delete_device(device_id: int, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        curr.execute(
            """
            SELECT container_name
            FROM devices
            WHERE device_id = %s;
            """,
            (device_id,),
        )
        row = curr.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Device not found")

        container_name = row[0]
        if container_name:
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.delete(
                        f"{AGENT_URL.rstrip('/')}/devices/{container_name}"
                    )
                    if response.status_code >= 400:
                        raise HTTPException(
                            status_code=502,
                            detail=f"Agent failed to remove container: {response.text}",
                        )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"Agent unavailable while removing container: {exc}",
                ) from exc

        curr.execute(
            "DELETE FROM devices WHERE device_id = %s RETURNING device_id;",
            (device_id,),
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
