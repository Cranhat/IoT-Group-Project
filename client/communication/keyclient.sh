#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CA_DIR="$SCRIPT_DIR/.tls-ca"
WORK_DIR="$(mktemp -d)"
CLIENT_OUT="$ROOT_DIR/src/communication"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

mkdir -p "$CLIENT_OUT"

if [[ ! -f "$CA_DIR/ca.key" || ! -f "$CA_DIR/ca.pem" ]]; then
  "$SCRIPT_DIR/genca.sh"
fi

cat > "$WORK_DIR/client.ext" <<'EOF'
[client_cert]
extendedKeyUsage=clientAuth
keyUsage=digitalSignature,keyEncipherment
EOF

openssl genrsa -out "$WORK_DIR/client0.key" 2048
openssl req -new -key "$WORK_DIR/client0.key" -out "$WORK_DIR/client0.csr" \
  -subj "/C=PL/ST=DN/L=Wroc/O=IoT-Group-Project/OU=Client/CN=pi-node-01/emailAddress="
openssl x509 -req -in "$WORK_DIR/client0.csr" \
  -CA "$CA_DIR/ca.pem" -CAkey "$CA_DIR/ca.key" -CAcreateserial \
  -out "$WORK_DIR/client0.crt" -days 365 -sha256 \
  -extfile "$WORK_DIR/client.ext" -extensions client_cert

cp "$WORK_DIR/client0.key" "$CLIENT_OUT/client0.key"
cp "$WORK_DIR/client0.crt" "$CLIENT_OUT/client0.crt"
cp "$CA_DIR/ca.pem" "$CLIENT_OUT/ca.pem"

echo "[OK] Generated client certs in $CLIENT_OUT"
