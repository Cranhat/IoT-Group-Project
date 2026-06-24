import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from database.src.database import Database

router = APIRouter(tags=["devices"])

db_instance = Database()
AGENT_URL = os.getenv("AGENT_URL", "http://agent:9000")


class Device(BaseModel):
    status: str
    ip_address: str
    container_name: Optional[str] = None
    device_name: Optional[str] = None


class DeviceStatusUpdate(BaseModel):
    status: str


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


@router.post("/devices/register")
def register_device(request: Device, db=Depends(db_instance.get_db)):
    """
    Upsert a device by ip_address. Called by the IoT server when a client
    connects. Returns the device_id so the server can reference it later.
    """
    conn, curr = db

    try:
        curr.execute("""
            INSERT INTO devices (status, ip_address, container_name, device_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ip_address) DO UPDATE
                SET status         = EXCLUDED.status,
                    container_name = EXCLUDED.container_name,
                    device_name    = EXCLUDED.device_name
            RETURNING device_id;
        """, (
            request.status,
            request.ip_address,
            request.container_name,
            request.device_name,
        ))

        device_id = curr.fetchone()[0]
        conn.commit()

        return {"device_id": device_id}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/devices/by-ip/{ip_address}/status")
def update_device_status_by_ip(ip_address: str, request: DeviceStatusUpdate, db=Depends(db_instance.get_db)):
    """Update only the status field for a device identified by IP. Called by the IoT server."""
    conn, curr = db

    try:
        curr.execute("""
            UPDATE devices
            SET status = %s
            WHERE ip_address = %s
            RETURNING device_id;
        """, (request.status, ip_address))

        row = curr.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")

        conn.commit()
        return {"device_id": row[0], "status": request.status}

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
