# IoT Device Agent

HTTP agent that provisions peripheral IoT devices as Docker containers.

## Flow

1. Generate a unique device id and TLS client certificate.
2. `docker create` a new container from `iot-client:latest`.
3. `docker cp` CA and client certificates into `/certs/`.
4. `docker start` the container.
5. Register the device in the backend API.

## Endpoints

- `POST /provision` — body: `{ "device_name": "sensor-01" }`
- `GET /provision/{container_name}/status`
- `DELETE /devices/{container_name}`

## Run via Docker Compose

```bash
# Provision a real peripheral device container
docker compose exec agent python scripts/provision_device.py sensor-01

# Mock mode (registers device in DB without Docker)
docker compose exec -e PROVISION_MOCK=true agent python scripts/provision_device.py sensor-01

# Call agent HTTP API from backend container
docker compose exec backend python -c "
import httpx
print(httpx.post('http://agent:9000/provision', json={'device_name': 'sensor-02'}).json())
"
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://backend:8000` | FastAPI backend |
| `CLIENT_IMAGE` | `iot-client:latest` | Client image tag |
| `DOCKER_NETWORK` | auto-detect | Docker network shared with `server` |
| `PROVISION_MOCK` | `false` | Skip Docker and simulate provisioning |
| `CA_DIR` | `../communication` | CA and server certificates |
| `TLS_SERVER_HOSTNAME` | `serv` | Must match server certificate CN |

## Certificates

If `communication/ca.pem` and `ca.key` are missing, the agent generates a development PKI on first provision.

Per-device client certificates are stored in `agent/certs/clients/<device_id>/`.
