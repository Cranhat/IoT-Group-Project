import logging
import subprocess
from typing import Any

from config import CLIENT_IMAGE, CONTAINER_PREFIX, DOCKER_NETWORK, SERVER_HOST, SERVER_PORT
from config import TLS_SERVER_HOSTNAME, USE_TLS

logger = logging.getLogger(__name__)


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    logger.debug("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Docker command failed ({' '.join(cmd)}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result


def docker_available() -> bool:
    try:
        result = _run(["docker", "info"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def resolve_network() -> str:
    if DOCKER_NETWORK:
        return DOCKER_NETWORK

    for container in ("iot_server", "server"):
        result = _run(
            [
                "docker", "inspect", "-f",
                "{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}",
                container,
            ],
            check=False,
        )
        network = result.stdout.strip()
        if result.returncode == 0 and network:
            return network

    raise RuntimeError(
        "Could not detect Docker network. Set DOCKER_NETWORK in .env "
        "(e.g. iot-group-project_default)."
    )


def container_exists(container_name: str) -> bool:
    result = _run(
        ["docker", "ps", "-a", "--filter", f"name=^{container_name}$", "--format", "{{.Names}}"],
        check=False,
    )
    return container_name in result.stdout.splitlines()


def get_container_status(container_name: str) -> str:
    if not container_exists(container_name):
        return "not_found"

    result = _run(
        ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def create_device_container(
    container_name: str,
    device_id: str,
    cert_paths: dict[str, str],
) -> dict[str, Any]:
    network = resolve_network()

    if container_exists(container_name):
        raise RuntimeError(f"Container already exists: {container_name}")

    env_args = [
        "-e", f"SERVER_HOST={SERVER_HOST}",
        "-e", f"PORT={SERVER_PORT}",
        "-e", f"DEVICE_ID={device_id}",
        "-e", f"USE_TLS={'true' if USE_TLS else 'false'}",
        "-e", "CA_CERT=/certs/ca.pem",
        "-e", "CLIENT_CERT=/certs/client.crt",
        "-e", "CLIENT_KEY=/certs/client.key",
        "-e", f"TLS_SERVER_HOSTNAME={TLS_SERVER_HOSTNAME}",
    ]

    create_cmd = [
        "docker", "create",
        "-i", "-t",
        "--name", container_name,
        "--network", network,
        "--restart", "unless-stopped",
        *env_args,
        CLIENT_IMAGE,
    ]
    _run(create_cmd)

    _run(["docker", "cp", cert_paths["ca_cert"], f"{container_name}:/certs/ca.pem"])
    _run(["docker", "cp", cert_paths["client_cert"], f"{container_name}:/certs/client.crt"])
    _run(["docker", "cp", cert_paths["client_key"], f"{container_name}:/certs/client.key"])

    _run(["docker", "start", container_name])

    return {
        "container_name": container_name,
        "device_id": device_id,
        "network": network,
        "status": get_container_status(container_name),
    }


def remove_device_container(container_name: str) -> None:
    if not container_exists(container_name):
        return

    _run(["docker", "rm", "-f", container_name], check=False)
