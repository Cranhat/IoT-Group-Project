# IoT-Group-Project

### Requirements
- Python 3.10+
- Node.js 18+ (with npm)
- PostgreSQL database

### Create a virtual environment && install needed tools (bash):
cd backend/database
python -m venv venv

    Windows:    venv\Scripts\activate
    Linux:      source venv/bin/activate

pip install fastapi uvicorn psycopg2-binary

### Create a database connection:
python backend/main.py

### Run Vue server:
cd frontend
npm install
npm run dev

### Run full stack with Docker:
cp .env.example .env
docker compose up --build

### Provision a peripheral device (Docker):
1. Open Admin Panel in the frontend.
2. Click **Provision Docker Device**.
3. The agent creates a new client container, copies TLS certs with `docker cp`, and registers the device.

CLI alternative (inside Docker, no local Python needed):
```bash
docker compose exec agent python scripts/provision_device.py sensor-01
```

Mock mode (no new container created):
```bash
docker compose exec -e PROVISION_MOCK=true agent python scripts/provision_device.py sensor-01
```

### Server-Client setup & connection
Both services are launched automatically along with all docker setup process \[`docker compose up --build`\].
1. First docker sets up TLS encryption process using `cert_gen` service that generates all the necessary keys and certificates.
2. `client` and `server` services wait for the certification set-up process to be completed.
3. Then above services are launched consecutively.

To access `client` and `server` services run:
- `docker attach iot_client`
- `docker attach iot_server`

Command available on the server (server sends them to client for execution in remote environment):
- `send <code>` - sends one-line Python scripts to client for execution
- `file <path>` - sends full .py file to client for execution \(root of the path is in the *server/src* directory\)
- `status` - prints client's status information
- `quit` - exits server app