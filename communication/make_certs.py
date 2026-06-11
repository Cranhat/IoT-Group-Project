#!/usr/bin/env python3
"""
Generate TLS materials for the IoT project using Python's cryptography library.

Outputs:
  communication/.tls-ca/ca.key   — CA private key (keep secret)
  communication/.tls-ca/ca.pem   — CA certificate

  server/src/communication/server.key  — server private key
  server/src/communication/server.crt  — server certificate (SAN: DNS:serv, DNS:localhost, IP:127.0.0.1)
  server/src/communication/ca.pem      — CA cert copy

  client/src/communication/client0.key — client private key
  client/src/communication/client0.crt — client certificate
  client/src/communication/ca.pem      — CA cert copy

Usage (from project root):
  python3 communication/make_certs.py
"""

import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR   = SCRIPT_DIR.parent

CA_DIR     = SCRIPT_DIR / ".tls-ca"
SERVER_OUT = ROOT_DIR / "server" / "src" / "communication"
CLIENT_OUT = ROOT_DIR / "client" / "src" / "communication"

for d in (CA_DIR, SERVER_OUT, CLIENT_OUT):
    d.mkdir(parents=True, exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _rsa_key(bits: int = 2048) -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=bits)

def _save_key(key, path: Path) -> None:
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    print(f"  wrote {path}")

def _save_cert(cert, path: Path) -> None:
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"  wrote {path}")

def _subject(**kwargs) -> x509.Name:
    attrs = [
        x509.NameAttribute(NameOID.COUNTRY_NAME,              kwargs.get("C",  "PL")),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,    kwargs.get("ST", "DN")),
        x509.NameAttribute(NameOID.LOCALITY_NAME,             kwargs.get("L",  "Wroc")),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,         kwargs.get("O",  "IoT-Group-Project")),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME,  kwargs.get("OU", "")),
        x509.NameAttribute(NameOID.COMMON_NAME,               kwargs.get("CN", "")),
    ]
    return x509.Name(attrs)

_NOW  = datetime.datetime.now(datetime.timezone.utc)
_YEAR = datetime.timedelta(days=365)

# ── 1. Certificate Authority ──────────────────────────────────────────────────

print("[1/3] Generating CA …")
ca_key  = _rsa_key(4096)
ca_subj = _subject(OU="CA", CN="IoT-Group-Project-CA")

ca_ski = x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key())

ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_subj)
    .issuer_name(ca_subj)
    .public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(_NOW)
    .not_valid_after(_NOW + datetime.timedelta(days=3650))
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .add_extension(ca_ski, critical=False)
    .add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    )
    .add_extension(
        x509.KeyUsage(
            digital_signature=False, key_encipherment=False,
            content_commitment=False, key_agreement=False,
            key_cert_sign=True, crl_sign=True,
            encipher_only=False, decipher_only=False,
            data_encipherment=False,
        ),
        critical=True,
    )
    .sign(ca_key, hashes.SHA256())
)

_save_key(ca_key,  CA_DIR / "ca.key")
_save_cert(ca_cert, CA_DIR / "ca.pem")

# ── 2. Server certificate ─────────────────────────────────────────────────────

print("[2/3] Generating server cert …")
srv_key  = _rsa_key()
srv_subj = _subject(OU="Server", CN="serv")

srv_cert = (
    x509.CertificateBuilder()
    .subject_name(srv_subj)
    .issuer_name(ca_subj)
    .public_key(srv_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(_NOW)
    .not_valid_after(_NOW + _YEAR)
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(
        x509.SubjectKeyIdentifier.from_public_key(srv_key.public_key()), critical=False
    )
    .add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    )
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("serv"),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]),
        critical=False,
    )
    .add_extension(
        x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False
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

_save_key(srv_key,   SERVER_OUT / "server.key")
_save_cert(srv_cert, SERVER_OUT / "server.crt")
_save_cert(ca_cert,  SERVER_OUT / "ca.pem")

# ── 3. Client certificate ─────────────────────────────────────────────────────

print("[3/3] Generating client cert …")
cli_key  = _rsa_key()
cli_subj = _subject(OU="Client", CN="pi-node-01")

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

_save_key(cli_key,   CLIENT_OUT / "client0.key")
_save_cert(cli_cert, CLIENT_OUT / "client0.crt")
_save_cert(ca_cert,  CLIENT_OUT / "ca.pem")

print("\n[OK] TLS materials generated for server and client.")
print(f"     CA:     {CA_DIR}")
print(f"     Server: {SERVER_OUT}")
print(f"     Client: {CLIENT_OUT}")
