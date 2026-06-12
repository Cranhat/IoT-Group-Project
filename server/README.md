# Server

The runnable server lives in `server/src/`.

## Run

1. Install dependencies: none beyond the Python standard library.
2. Generate TLS files if `USE_TLS = True` (run once from the project root):
```bash
python3 communication/make_certs.py
```
3. Start the server from `server/src/`:
```bash
python server.py
```

## Files

- `src/server.py` - server entry point.
- `src/config.py` - server settings.
- `src/protocol.py` - JSON message helpers.
- `src/communication/` - TLS key generation output for the server.
