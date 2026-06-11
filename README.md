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