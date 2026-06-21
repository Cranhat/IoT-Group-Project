# IoT-Group-Project

Platforma IoT do bezpiecznej komunikacji z urządzeniami brzegowymi — panel webowy, REST API, provisioning kontenerów Docker, kanał TLS server↔client oraz monitorowanie ruchu sieciowego.

## Wymagania

- Python 3.10+
- Node.js 18+ (npm)
- Docker i Docker Compose (zalecane)
- PostgreSQL (przy uruchomieniu lokalnym bez Docker)

## Szybki start (Docker)

```bash
cp .env.example .env
# Uzupełnij POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose up --build
```

| Serwis | Adres |
|--------|-------|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Agent | http://localhost:9000 |

Domyślne konto administratora (tworzone przy pierwszym starcie): `admin` / `1234`.

Pełna dokumentacja: [docs/documentation/docs/index.md](docs/documentation/docs/index.md) (MkDocs).

## Uruchomienie lokalne (bez Docker)

### Backend

```bash
cd backend/database
python -m venv venv
source venv/bin/activate          # Linux
# venv\Scripts\activate           # Windows
pip install -r ../requirements.txt

# Ustaw POSTGRES_* i DB_HOST=localhost
uvicorn api.app:app --reload --app-dir ../
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Provisioning urządzenia (Docker)

1. Zaloguj się jako administrator w frontendzie.
2. Otwórz **Admin Panel** → **Provision Docker Device**.
3. Agent tworzy kontener klienta, kopiuje certyfikaty TLS i rejestruje urządzenie w bazie.

CLI:

```bash
docker compose exec agent python scripts/provision_device.py sensor-01
```

Tryb mock (bez nowego kontenera):

```bash
docker compose exec -e PROVISION_MOCK=true agent python scripts/provision_device.py sensor-01
```

## Server ↔ Client

Serwisy startują automatycznie w Docker Compose:

1. `cert_gen` generuje certyfikaty TLS.
2. `server` i `client` startują po zakończeniu `cert_gen`.

Interakcja z CLI serwera:

```bash
docker attach iot_server
```

Polecenia:

| Polecenie | Opis |
|-----------|------|
| `send <code>` | Wyślij jednolinijkowy skrypt Python |
| `file <path>` | Wyślij plik `.py` (ścieżka względem `server/src/`) |
| `status` | Pokaż stan klienta |
| `quit` | Zakończ serwer |

Logi klienta: `docker attach iot_client`

## Testy

```bash
pip install -r backend/requirements.txt
PYTHONPATH=backend:. python -m pytest
```

## Struktura projektu

```
backend/          FastAPI + PostgreSQL
frontend/         Vue 3 + Vite
server/           Serwer TLS (zadania IoT)
client/           Klient urządzenia
agent/            Provisioning Docker
packet_sniffer/   Monitorowanie ruchu TCP
communication/    Certyfikaty TLS
docs/documentation/  Dokumentacja MkDocs
```

## Zespół

Cyprian Burdzy, Nicole Jarczewska, Natalia Kułak, Oleh Marushchak, Tomek Piaseczny
