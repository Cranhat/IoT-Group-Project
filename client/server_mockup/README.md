# Server mockup

The runnable server lives in `client/server_mockup/src/`.

## Run

1. Install dependencies: none beyond the Python standard library.
2. Generate TLS files if `USE_TLS = True`:
```bash
bash ../../communication/setup_all.sh
```
3. Start the server from `client/server_mockup/src/`:
```bash
python server.py
```

## Files

- `src/server.py` - server entry point.
- `src/config.py` - server settings.
- `src/protocol.py` - JSON message helpers.
- `src/communication/` - TLS key generation output for the server.
