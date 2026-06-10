import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


SERVER_HOST = os.getenv("SERVER_HOST", "localhost")  # Change to the server machine's LAN IP or DNS name.
PORT = int(os.getenv("PORT", "5000"))
DEVICE_ID = os.getenv("DEVICE_ID", "pi-node-01")
TLS_SERVER_HOSTNAME = os.getenv("TLS_SERVER_HOSTNAME", SERVER_HOST)

USE_TLS = env_bool("USE_TLS", False)

CERT_DIR = Path(os.getenv("CERT_DIR", BASE_DIR / "certs"))
CA_CERT = os.getenv("CA_CERT", str(CERT_DIR / "ca.crt"))
SERVER_CERT = os.getenv("SERVER_CERT", str(CERT_DIR / "server.crt"))
SERVER_KEY = os.getenv("SERVER_KEY", str(CERT_DIR / "server.key"))
CLIENT_CERT = os.getenv("CLIENT_CERT", str(CERT_DIR / "client.crt"))
CLIENT_KEY = os.getenv("CLIENT_KEY", str(CERT_DIR / "client.key"))

HEARTBEAT_INTERVAL = 5  # seconds
USE_DOCKER_SANDBOX = False  # Set True if you run tasks inside Docker.
