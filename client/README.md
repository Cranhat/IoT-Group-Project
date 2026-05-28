# Client

The runnable client lives in `client/src/`.

## Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Generate TLS files if `USE_TLS = True`:
```bash
bash ../communication/setup_all.sh
```
3. Start the client from `client/src/`:
```bash
python client.py
```

## Files

- `src/client.py` - client entry point.
- `src/config.py` - client settings.
- `src/protocol.py` - JSON message helpers.
- `src/task_exec.py` - task queue and execution helpers.
- `communication/` - TLS key generation scripts.
