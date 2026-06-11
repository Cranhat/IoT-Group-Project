import os
from pathlib import Path


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

CA_DIR = Path(os.getenv("CA_DIR", PROJECT_ROOT / "communication"))
CLIENT_CERTS_DIR = Path(os.getenv("CLIENT_CERTS_DIR", BASE_DIR / "certs" / "clients"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
AGENT_PORT = int(os.getenv("AGENT_PORT", "9000"))

CLIENT_IMAGE = os.getenv("CLIENT_IMAGE", "iot-client:latest")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "")
SERVER_HOST = os.getenv("SERVER_HOST", "server")
SERVER_PORT = os.getenv("SERVER_PORT", "5000")
TLS_SERVER_HOSTNAME = os.getenv("TLS_SERVER_HOSTNAME", "serv")
USE_TLS = env_bool("USE_TLS", True)

PROVISION_MOCK = env_bool("PROVISION_MOCK", False)
CONTAINER_PREFIX = os.getenv("CONTAINER_PREFIX", "iot_client_")
