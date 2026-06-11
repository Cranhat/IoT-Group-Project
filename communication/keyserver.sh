#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CA_DIR="$SCRIPT_DIR/.tls-ca"
WORK_DIR="$(mktemp -d)"
SERVER_OUT="$ROOT_DIR/server/src/communication"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

mkdir -p "$SERVER_OUT"

if [[ ! -f "$CA_DIR/ca.key" || ! -f "$CA_DIR/ca.pem" ]]; then
  "$SCRIPT_DIR/genca.sh"
fi

cat > "$WORK_DIR/server.ext" <<'EOF'
[server_cert]
subjectAltName=DNS:serv,DNS:localhost,IP:127.0.0.1
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
EOF

openssl genrsa -out "$WORK_DIR/server.key" 2048
openssl req -new -key "$WORK_DIR/server.key" -out "$WORK_DIR/server.csr" \
  -subj "/C=PL/ST=DN/L=Wroc/O=IoT-Group-Project/OU=Server/CN=serv/emailAddress="
openssl x509 -req -in "$WORK_DIR/server.csr" \
  -CA "$CA_DIR/ca.pem" -CAkey "$CA_DIR/ca.key" -CAcreateserial \
  -out "$WORK_DIR/server.crt" -days 365 -sha256 \
  -extfile "$WORK_DIR/server.ext" -extensions server_cert

cp "$WORK_DIR/server.key" "$SERVER_OUT/server.key"
cp "$WORK_DIR/server.crt" "$SERVER_OUT/server.crt"
cp "$CA_DIR/ca.pem" "$SERVER_OUT/ca.pem"

echo "[OK] Generated server certs in $SERVER_OUT"
