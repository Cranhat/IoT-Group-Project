import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from provisioner import deprovision_device, get_provision_status, provision_device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IoT Device Agent")


class ProvisionRequest(BaseModel):
    device_name: str | None = None


@app.get("/")
def health():
    return {"service": "iot-device-agent", "status": "ok"}


@app.post("/provision")
def provision(request: ProvisionRequest):
    try:
        result = provision_device(request.device_name)
        return {"message": "Device provisioned", **result}
    except Exception as exc:
        logger.exception("Provision failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/provision/{container_name}/status")
def provision_status(container_name: str):
    try:
        return get_provision_status(container_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/devices/{container_name}")
def remove_device(container_name: str):
    try:
        return deprovision_device(container_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
