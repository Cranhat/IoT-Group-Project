import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

USE_TLS = env_bool("USE_TLS", False)

CERT_DIR = Path(os.getenv("CERT_DIR", BASE_DIR / "certs"))
CA_CERT = os.getenv("CA_CERT", str(CERT_DIR / "ca.crt"))
SERVER_CERT = os.getenv("SERVER_CERT", str(CERT_DIR / "server.crt"))
SERVER_KEY = os.getenv("SERVER_KEY", str(CERT_DIR / "server.key"))
