import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")
PORT      = int(os.environ.get("PORT", "3000"))

USE_TLS = os.environ.get("USE_TLS", "true").lower() in ("1", "true", "yes")

# Cert paths — defaults to the communication/ subdir next to this file.
# Overridden by environment variables in Docker.
_COMM_DIR  = BASE_DIR / "communication"
CA_CERT     = os.environ.get("CA_CERT",     str(_COMM_DIR / "ca.pem"))
SERVER_CERT = os.environ.get("SERVER_CERT", str(_COMM_DIR / "server.crt"))
SERVER_KEY  = os.environ.get("SERVER_KEY",  str(_COMM_DIR / "server.key"))
