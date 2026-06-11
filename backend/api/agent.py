import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.src.database import Database

router = APIRouter(tags=["agent"])

AGENT_URL = os.getenv("AGENT_URL", "http://agent:9000")
db_instance = Database()


class ProvisionRequest(BaseModel):
    device_name: str | None = None


@router.post("/devices/provision")
async def provision_device(request: ProvisionRequest):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{AGENT_URL.rstrip('/')}/provision",
                json=request.model_dump(),
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


@router.get("/devices/provision/{container_name}/status")
async def provision_status(container_name: str):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{AGENT_URL.rstrip('/')}/provision/{container_name}/status"
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@router.delete("/devices/provision/{container_name}")
async def deprovision_device(container_name: str, db=Depends(db_instance.get_db)):
    conn, curr = db

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.delete(
                f"{AGENT_URL.rstrip('/')}/devices/{container_name}"
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Agent unavailable: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    curr.execute(
        "DELETE FROM devices WHERE container_name = %s RETURNING device_id;",
        (container_name,),
    )
    deleted = curr.fetchone()
    conn.commit()

    return {
        "message": "Device deprovisioned",
        "container_name": container_name,
        "device_id": deleted[0] if deleted else None,
        "agent": response.json(),
    }
