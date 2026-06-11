import logging
import subprocess
from pathlib import Path

from config import CA_DIR, CLIENT_CERTS_DIR, TLS_SERVER_HOSTNAME

logger = logging.getLogger(__name__)


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({' '.join(cmd)}): {result.stderr.strip() or result.stdout.strip()}"
        )


def ensure_ca_exists() -> None:
    ca_pem = CA_DIR / "ca.pem"
    ca_key = CA_DIR / "ca.key"

    if ca_pem.exists() and ca_key.exists():
        return

    CA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Generating development CA in %s", CA_DIR)

    _run(["openssl", "genrsa", "-out", "ca.key", "4096"], cwd=CA_DIR)
    _run(
        [
            "openssl", "req", "-x509", "-new", "-nodes",
            "-key", "ca.key", "-sha256", "-days", "3650",
            "-out", "ca.pem",
            "-subj", "/CN=IoT-Project-CA",
        ],
        cwd=CA_DIR,
    )

    server_crt = CA_DIR / "server.crt"
    server_key = CA_DIR / "server.key"
    if not server_crt.exists() or not server_key.exists():
        _run(["openssl", "genrsa", "-out", "server.key", "2048"], cwd=CA_DIR)
        _run(
            [
                "openssl", "req", "-new", "-key", "server.key",
                "-out", "server.csr",
                "-subj", f"/CN={TLS_SERVER_HOSTNAME}",
            ],
            cwd=CA_DIR,
        )
        _run(
            [
                "openssl", "x509", "-req", "-in", "server.csr",
                "-CA", "ca.pem", "-CAkey", "ca.key", "-CAcreateserial",
                "-out", "server.crt", "-days", "825", "-sha256",
            ],
            cwd=CA_DIR,
        )


def generate_client_cert(device_id: str) -> dict[str, str]:
    ensure_ca_exists()

    cert_dir = CLIENT_CERTS_DIR / device_id
    cert_dir.mkdir(parents=True, exist_ok=True)

    client_key = cert_dir / "client.key"
    client_csr = cert_dir / "client.csr"
    client_crt = cert_dir / "client.crt"

    if client_crt.exists() and client_key.exists():
        return {
            "ca_cert": str(CA_DIR / "ca.pem"),
            "client_cert": str(client_crt),
            "client_key": str(client_key),
        }

    _run(["openssl", "genrsa", "-out", "client.key", "2048"], cwd=cert_dir)
    _run(
        [
            "openssl", "req", "-new", "-key", "client.key",
            "-out", "client.csr",
            "-subj", f"/CN={device_id}",
        ],
        cwd=cert_dir,
    )
    _run(
        [
            "openssl", "x509", "-req", "-in", "client.csr",
            "-CA", str(CA_DIR / "ca.pem"),
            "-CAkey", str(CA_DIR / "ca.key"),
            "-CAcreateserial",
            "-out", "client.crt", "-days", "825", "-sha256",
        ],
        cwd=cert_dir,
    )

    return {
        "ca_cert": str(CA_DIR / "ca.pem"),
        "client_cert": str(client_crt),
        "client_key": str(client_key),
    }
