#!/usr/bin/env python3
"""
Provision a new client certificate signed by the existing project CA.

This script NEVER touches ca.key generation — it only signs a new client cert
using the CA that was already created by make_certs.py. Run make_certs.py first.

Usage (from project root):
  python3 communication/provision_client.py <device-id> <output-dir>

Examples:
  # Docker second client — writes into client2/src/communication/
  python3 communication/provision_client.py pi-node-02 client2/src/communication

  # Physical Pi — writes into /tmp/pi-node-02/ then scp to the device
  python3 communication/provision_client.py pi-node-02 /tmp/pi-node-02

Output files in <output-dir>:
  client0.key   — device private key  (transfer securely, e.g. via scp)
  client0.crt   — device certificate
  ca.pem        — CA certificate      (not secret, but keep it consistent)

The server trusts any cert signed by this CA — no server changes needed.
"""

import sys
import datetime
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
except ImportError:
    sys.exit("ERROR: run 'pip install cryptography' first.")

# ── Args ──────────────────────────────────────────────────────────────────────

if len(sys.argv) != 3:
    sys.exit(f"Usage: python3 {sys.argv[0]} <device-id> <output-dir>")

DEVICE_ID  = sys.argv[1]
OUTPUT_DIR = Path(sys.argv[2])
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load existing CA ──────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).resolve().parent
CA_KEY_PATH  = SCRIPT_DIR / ".tls-ca" / "ca.key"
CA_CERT_PATH = SCRIPT_DIR / ".tls-ca" / "ca.pem"

if not CA_KEY_PATH.exists() or not CA_CERT_PATH.exists():
    sys.exit(
        "ERROR: CA not found. Run 'python3 communication/make_certs.py' first "
        "to initialise the CA."
    )

ca_key  = serialization.load_pem_private_key(CA_KEY_PATH.read_bytes(), password=None)
ca_cert = x509.load_pem_x509_certificate(CA_CERT_PATH.read_bytes())
ca_subj = ca_cert.subject

print(f"[CA] Loaded from {CA_KEY_PATH}")

# ── Generate client key + cert ────────────────────────────────────────────────

_NOW  = datetime.datetime.now(datetime.timezone.utc)
_YEAR = datetime.timedelta(days=365)

cli_key  = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cli_subj = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME,             "PL"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,   "DN"),
    x509.NameAttribute(NameOID.LOCALITY_NAME,            "Wroc"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME,        "IoT-Group-Project"),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Client"),
    x509.NameAttribute(NameOID.COMMON_NAME,              DEVICE_ID),
])

cli_cert = (
    x509.CertificateBuilder()
    .subject_name(cli_subj)
    .issuer_name(ca_subj)
    .public_key(cli_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(_NOW)
    .not_valid_after(_NOW + _YEAR)
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(
        x509.SubjectKeyIdentifier.from_public_key(cli_key.public_key()), critical=False
    )
    .add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    )
    .add_extension(
        x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False
    )
    .add_extension(
        x509.KeyUsage(
            digital_signature=True, key_encipherment=True,
            content_commitment=False, key_agreement=False,
            key_cert_sign=False, crl_sign=False,
            encipher_only=False, decipher_only=False,
            data_encipherment=False,
        ),
        critical=True,
    )
    .sign(ca_key, hashes.SHA256())
)

# ── Write output ──────────────────────────────────────────────────────────────

key_path = OUTPUT_DIR / "client0.key"
crt_path = OUTPUT_DIR / "client0.crt"
ca_path  = OUTPUT_DIR / "ca.pem"

key_path.write_bytes(cli_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
))
key_path.chmod(0o600)

crt_path.write_bytes(cli_cert.public_bytes(serialization.Encoding.PEM))
ca_path.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))

print(f"[OK] Provisioned {DEVICE_ID}")
print(f"     {key_path}  (private — transfer securely)")
print(f"     {crt_path}")
print(f"     {ca_path}")
print()
print("To transfer to a physical device:")
print(f"  scp {key_path} {crt_path} {ca_path}  pi@<ip>:/home/pi/iot/client/src/communication/")
