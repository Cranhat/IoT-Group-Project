# TLS key scripts

Use these scripts to generate matching TLS files for the client and server.

## Scripts

- `genca.sh` — creates a shared CA in `communication/.tls-ca/`
- `keyserver.sh` — writes `server.crt`, `server.key`, and `ca.pem` to `server/src/communication/`
- `keyclient.sh` — writes `client0.crt`, `client0.key`, and `ca.pem` to `client/src/communication/`
- `setup_all.sh` — runs all three scripts in order

## Run (from project root)

```bash
python3 communication/make_certs.py
```

Requires the `cryptography` package (`pip install cryptography`).

## Notes

- All generated key/cert files are gitignored. Only the scripts and `make_certs.py` are tracked.
- The CA private key lives in `communication/.tls-ca/ca.key` — keep this secret.
- Re-run `make_certs.py` whenever you need fresh certificates.
- The legacy shell scripts (`setup_all.sh`, `genca.sh`, etc.) require `openssl` in PATH and do not produce the extensions required by Python 3.14. Use `make_certs.py` instead.
