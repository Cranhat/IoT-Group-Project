# Docker

Pełny stack uruchamia się jednym poleceniem:

```bash
cp .env.example .env
docker compose up --build
```

## Serwisy

| Serwis | Kontener | Opis |
|--------|----------|------|
| `db` | `iot_postgres` | PostgreSQL 16, wolumen `pgdata` |
| `backend` | `iot_fastapi` | FastAPI na porcie 8000, hot-reload |
| `frontend` | `iot_frontend` | Vue dev server na porcie 5173 |
| `cert_gen` | `iot_cert_gen` | Jednorazowe generowanie certyfikatów TLS |
| `server` | `iot_server` | Serwer IoT (port 5000), tryb interaktywny |
| `client` | `iot_client` | Domyślny klient urządzenia |
| `agent` | `iot_agent` | Provisioning kontenerów (port 9000) |
| `backend_sniffer` | `iot_backend_sniffer` | Sniffer ruchu backendu |
| `server_sniffer` | `iot_server_sniffer` | Sniffer ruchu serwera |

## Kolejność startu

1. `cert_gen` generuje certyfikaty TLS i kończy działanie.
2. `db` przechodzi healthcheck (`pg_isready`).
3. `backend` startuje po zdrowej bazie, inicjalizuje tabele.
4. `server` i `client` startują po `cert_gen`.
5. `agent`, sniffery i `frontend` startują po backendzie.

## Zmienne środowiskowe (`.env`)

| Zmienna | Opis |
|---------|------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Dane PostgreSQL (wymagane) |
| `HOST_PORT_FRONTEND` | Port frontendu na hoście (domyślnie 5173) |
| `HOST_PORT_BACKEND` | Port backendu na hoście (domyślnie 8000) |
| `HOST_PORT_AGENT` | Port agenta na hoście (domyślnie 9000) |
| `AGENT_URL` | URL agenta z perspektywy backendu |
| `DOCKER_NETWORK` | Sieć Docker (auto-wykrywana przez agenta, opcjonalna) |
| `PROVISION_MOCK` | `true` — provisioning bez tworzenia kontenera |
| `SERVER_PORT` | Port serwera IoT (domyślnie 5000) |
| `USE_TLS` | Włączenie TLS między server a client |
| `TLS_SERVER_HOSTNAME` | CN certyfikatu serwera (domyślnie `serv`) |
| `MONITORED_PORT`, `SNIFFER_TIMEOUT` | Konfiguracja sniffera |

## Interakcja z serwerem i klientem

```bash
docker attach iot_server   # CLI serwera (send, file, status, quit)
docker attach iot_client     # logi klienta
```

Polecenia serwera:

| Polecenie | Opis |
|-----------|------|
| `send <code>` | Wyślij jednolinijkowy skrypt Python |
| `file <path>` | Wyślij plik `.py` (ścieżka względem `server/src/`) |
| `status` | Pokaż ostatni stan klienta |
| `quit` | Zakończ serwer |

## Provisioning urządzenia

**Z UI:** Admin Panel → **Provision Docker Device**.

**CLI:**

```bash
docker compose exec agent python scripts/provision_device.py sensor-01
```

**Tryb mock (bez nowego kontenera):**

```bash
docker compose exec -e PROVISION_MOCK=true agent python scripts/provision_device.py sensor-01
```

## Certyfikaty TLS

Generowane automatycznie przez serwis `cert_gen` przy pierwszym `docker compose up`. Pliki trafiają do katalogu `communication/` (montowany jako `/certs` w kontenerach).

Ręczna regeneracja (poza Dockerem):

```bash
python3 communication/make_certs.py
```
