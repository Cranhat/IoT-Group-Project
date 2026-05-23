import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")  # Change to the server machine's LAN IP or DNS name.
PORT = int(os.getenv("PORT", "5000"))
DEVICE_ID = os.getenv("DEVICE_ID", "pi-node-01")

USE_TLS = False  # Set True when using real certs.

CERT_DIR = BASE_DIR / "certs"
CA_CERT = str(CERT_DIR / "ca.crt")
SERVER_CERT = str(CERT_DIR / "server.crt")
SERVER_KEY = str(CERT_DIR / "server.key")
CLIENT_CERT = str(CERT_DIR / "client.crt")
CLIENT_KEY = str(CERT_DIR / "client.key")

HEARTBEAT_INTERVAL = 5  # seconds
USE_DOCKER_SANDBOX = False  # Set True if you run tasks inside Docker.
