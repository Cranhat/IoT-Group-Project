# Server Bundle

Copy this entire `server/` directory to the server machine. The deployable code lives in `server/src/`.

## Run

1. Install dependencies: none beyond the Python standard library.
2. If you use TLS, place certificates in `src/certs/`.
3. Start the server from the `src/` directory:
   `python server.py`

## Layout

- `src/server.py` - active server entry point.
- `src/config.py` - server-side settings.
- `src/protocol.py` - shared newline-delimited JSON message helpers.
- `src/certs/` - optional TLS certificates if `USE_TLS = True`.
