import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")
PORT        = int(os.environ.get("PORT", "3000"))
DEVICE_ID   = os.environ.get("DEVICE_ID", "pi-node-01")

USE_TLS = os.environ.get("USE_TLS", "true").lower() in ("1", "true", "yes")
TLS_SERVER_HOSTNAME = os.environ.get("TLS_SERVER_HOSTNAME", "serv")

# Cert paths — defaults to the communication/ subdir next to this file.
# Overridden by environment variables in Docker.
_COMM_DIR   = BASE_DIR / "communication"
CA_CERT     = os.environ.get("CA_CERT",     str(_COMM_DIR / "ca.pem"))
CLIENT_CERT = os.environ.get("CLIENT_CERT", str(_COMM_DIR / "client0.crt"))
CLIENT_KEY  = os.environ.get("CLIENT_KEY",  str(_COMM_DIR / "client0.key"))

HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "5"))
USE_DOCKER_SANDBOX = os.environ.get("USE_DOCKER_SANDBOX", "false").lower() in ("1", "true", "yes")
