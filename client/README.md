# Client

The runnable client lives in `client/src/`.

## Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Generate TLS files if `USE_TLS = True`:
```bash
python3 ../communication/make_certs.py
```
3. Start the client from `client/src/`:
```bash
python client.py
```

In Docker, the client starts automatically as `iot_client` after `cert_gen` completes.

## Files

- `src/client.py` - client entry point, reconnect loop
- `src/config.py` - client settings
- `src/protocol.py` - JSON message helpers
- `src/task_exec.py` - task queue and execution helpers
- `src/communication/clientcomms.py` - TLS client socket

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `server` | Server hostname |
| `PORT` | `5000` | Server port |
| `USE_TLS` | `true` | Enable TLS |
| `CA_CERT` | `/certs/ca.pem` | CA certificate path |
| `CLIENT_CERT` | `/certs/client0.crt` | Client certificate |
| `CLIENT_KEY` | `/certs/client0.key` | Client private key |
| `TLS_SERVER_HOSTNAME` | `serv` | Server certificate CN |

Per-device certificates are copied into `/certs/` by the agent during provisioning.
