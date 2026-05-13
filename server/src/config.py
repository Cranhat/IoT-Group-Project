import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

USE_TLS = False  # Set True when using real certs.

CERT_DIR = BASE_DIR / "certs"
CA_CERT = str(CERT_DIR / "ca.crt")
SERVER_CERT = str(CERT_DIR / "server.crt")
SERVER_KEY = str(CERT_DIR / "server.key")
