#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_DIR="$SCRIPT_DIR/.tls-ca"

mkdir -p "$CA_DIR"

openssl genrsa -out "$CA_DIR/ca.key" 4096
openssl req -x509 -new -nodes -key "$CA_DIR/ca.key" -sha256 -days 3650 \
  -out "$CA_DIR/ca.pem" \
  -subj "/C=PL/ST=DN/L=Wroc/O=IoT-Group-Project/OU=CA/CN=IoT-Group-Project-CA/emailAddress="

echo "[OK] Generated CA at $CA_DIR"
