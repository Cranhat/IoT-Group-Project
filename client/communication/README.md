# TLS key scripts

Use these scripts to generate matching TLS files for the client and server mockup.

## Scripts

- `genca.sh` creates a shared CA in `client/communication/.tls-ca/`
- `keyserver.sh` writes `server.crt`, `server.key`, and `ca.pem` to `client/server_mockup/src/communication/`
- `keyclient.sh` writes `client0.crt`, `client0.key`, and `ca.pem` to `client/src/communication/`
- `setup_all.sh` runs all three scripts in order

## Run

```bash
bash setup_all.sh
```
