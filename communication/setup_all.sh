#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/genca.sh"
"$SCRIPT_DIR/keyserver.sh"
"$SCRIPT_DIR/keyclient.sh"

echo "[OK] TLS materials generated for both server and client"
