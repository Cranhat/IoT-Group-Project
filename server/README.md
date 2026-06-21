# Server

The runnable server lives in `server/src/`.

## Run

1. Generate TLS files if `USE_TLS = True` (run once from the project root):
```bash
python3 communication/make_certs.py
```
2. Start the server from `server/src/`:
```bash
python server.py
```

In Docker, the server starts automatically as `iot_server` after `cert_gen` completes.

Interactive CLI:

```bash
docker attach iot_server
```

Commands: `send <code>`, `file <path>`, `status`, `quit`.

## Files

- `src/server.py` - server entry point and CLI
- `src/config.py` - server settings
- `src/protocol.py` - JSON message helpers
- `src/communication/comms.py` - TLS server socket

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `BIND_HOST` | `0.0.0.0` | Bind address |
| `PORT` | `5000` | Listen port |
| `USE_TLS` | `true` | Enable TLS |
| `CA_CERT` | `/certs/ca.pem` | CA certificate |
| `SERVER_CERT` | `/certs/server.crt` | Server certificate |
| `SERVER_KEY` | `/certs/server.key` | Server private key |

See [communication documentation](../docs/documentation/docs/communication.md) for protocol details.
