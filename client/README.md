# Client Bundle

Copy this entire `client/` directory to the client machine. The deployable code lives in `client/src/`.

## Run

1. Install dependencies:
   `pip install -r requirements.txt`
2. Edit `src/config.py` and set `SERVER_HOST` to the server machine's IP or DNS name.
3. Start the client from the `src/` directory:
   `python client.py`

## Layout

- `src/client.py` - active client entry point.
- `src/client_old.py` - legacy client version kept for reference.
- `src/config.py` - client-side settings.
- `src/protocol.py` - shared newline-delimited JSON message helpers.
- `src/task_exec.py` - code responsible for task queue management and task execution.
- `src/certs/` - optional TLS certificates if `USE_TLS = True`.
