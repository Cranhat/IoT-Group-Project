import logging
import uuid
from typing import Any

import httpx

from certs import generate_client_cert
from config import BACKEND_URL, CONTAINER_PREFIX, PROVISION_MOCK
from docker_manager import create_device_container, docker_available, get_container_status, remove_device_container

logger = logging.getLogger(__name__)


def _make_device_id(device_name: str | None) -> str:
    suffix = uuid.uuid4().hex[:8]
    if device_name:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in device_name.lower())
        safe = safe.strip("-")[:24] or "device"
        return f"{safe}-{suffix}"
    return f"pi-{suffix}"


def _normalize_device_status(status: str) -> str:
    if status in {"running", "created"}:
        return "online"
    if status in {"exited", "dead"}:
        return "offline"
    return status


def _register_device_in_backend(
    device_id: str,
    container_name: str,
    device_name: str | None,
    status: str,
) -> dict[str, Any] | None:
    payload = {
        "status": _normalize_device_status(status),
        "ip_address": device_id,
        "container_name": container_name,
        "device_name": device_name or device_id,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(f"{BACKEND_URL.rstrip('/')}/add/devices", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.warning("Failed to register device in backend: %s", exc)
        return None


def provision_device(device_name: str | None = None) -> dict[str, Any]:
    device_id = _make_device_id(device_name)
    container_name = f"{CONTAINER_PREFIX}{device_id}"

    if PROVISION_MOCK or not docker_available():
        logger.info("Provisioning in mock mode for %s", device_id)
        backend_record = _register_device_in_backend(
            device_id, container_name, device_name, "online"
        )
        return {
            "mode": "mock",
            "device_id": device_id,
            "container_name": container_name,
            "device_name": device_name or device_id,
            "status": "online",
            "backend": backend_record,
        }

    cert_paths = generate_client_cert(device_id)
    container_info = create_device_container(container_name, device_id, cert_paths)
    backend_record = _register_device_in_backend(
        device_id,
        container_name,
        device_name,
        container_info["status"],
    )

    return {
        "mode": "docker",
        "device_id": device_id,
        "container_name": container_name,
        "device_name": device_name or device_id,
        "status": container_info["status"],
        "network": container_info["network"],
        "backend": backend_record,
    }


def get_provision_status(container_name: str) -> dict[str, Any]:
    if PROVISION_MOCK or not docker_available():
        return {
            "container_name": container_name,
            "status": "online",
            "mode": "mock",
        }

    return {
        "container_name": container_name,
        "status": get_container_status(container_name),
        "mode": "docker",
    }


def deprovision_device(container_name: str) -> dict[str, Any]:
    if PROVISION_MOCK or not docker_available():
        return {"container_name": container_name, "removed": True, "mode": "mock"}

    remove_device_container(container_name)
    return {"container_name": container_name, "removed": True, "mode": "docker"}
