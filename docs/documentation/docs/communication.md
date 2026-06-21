# Communication

Warstwa komunikacji między urządzeniami IoT oraz usługami wspierającymi.

## Server (`server/`)

Serwer nasłuchuje na porcie 5000 (domyślnie), akceptuje **jedno** połączenie klienta i obsługuje interaktywne CLI.

**Uruchomienie (Docker):** automatycznie jako `iot_server`.

**Uruchomienie lokalne:**

```bash
python3 communication/make_certs.py
cd server/src
python server.py
```

**Pliki kluczowe:**

| Plik | Opis |
|------|------|
| `server/src/server.py` | Główna pętla, CLI |
| `server/src/protocol.py` | Serializacja JSON + newline |
| `server/src/communication/comms.py` | TLS server socket |
| `server/src/config.py` | `BIND_HOST`, `PORT`, `USE_TLS`, ścieżki certów |

## Client (`client/`)

Klient łączy się z serwerem, wysyła heartbeat ze statusem urządzenia i wykonuje zadania Python z kolejki.

**Uruchomienie lokalne:**

```bash
pip install -r requirements.txt
python3 communication/make_certs.py
cd client/src
python client.py
```

**Pliki kluczowe:**

| Plik | Opis |
|------|------|
| `client/src/client.py` | Połączenie, wątki, reconnect |
| `client/src/task_exec.py` | Kolejka zadań, `subprocess` |
| `client/src/communication/clientcomms.py` | TLS client socket |
| `client/src/config.py` | `SERVER_HOST`, `PORT`, certyfikaty |

Klient automatycznie reconnectuje z exponential backoff (2s → max 60s).

## Agent (`agent/`)

HTTP API do dynamicznego tworzenia kontenerów-urządzeń.

| Endpoint | Opis |
|----------|------|
| `POST /provision` | Utwórz urządzenie (`device_name` opcjonalne) |
| `GET /provision/{container_name}/status` | Status kontenera |
| `DELETE /devices/{container_name}` | Usuń kontener |

Flow provisioningu:

1. Generacja `device_id` i certyfikatu klienta.
2. `docker create` + `docker cp` certów + `docker start`.
3. Rejestracja w backendzie (`POST /add/devices`).

Szczegóły: `agent/README.md`.

## Certyfikaty TLS (`communication/`)

| Skrypt / plik | Opis |
|---------------|------|
| `make_certs.py` | Główny generator (Python, `cryptography`) |
| `setup_all.sh` | Legacy (wymaga OpenSSL) |
| `communication/ca.pem` | Certyfikat CA (generowany, gitignored) |
| `communication/server.crt`, `server.key` | Cert serwera |
| `communication/client0.crt`, `client0.key` | Cert domyślnego klienta |

Przy `USE_TLS=true` obie strony wymagają ważnych certyfikatów podpisanych przez wspólną CA.

## Packet sniffer (`packet_sniffer/`)

Sniffer filtruje ruch TCP na `MONITORED_PORT`, dekoduje payload i wysyła do backendu:

```
POST /tables/packet_sniffer_logs
{
  "sniffer_name": "backend_sniffer",
  "port": 8000,
  "log": "...",
  "timestamp": "..."
}
```

Wymaga uprawnień `NET_ADMIN` / `NET_RAW` (ustawione w `docker-compose.yaml`).

Dwa warianty:

- `backend_sniffer` — `network_mode: service:backend`, port 8000
- `server_sniffer` — `network_mode: service:server`, port 5000

## Protokół wiadomości

Format: JSON + `\n` (UTF-8).

Przykład zadania (server → client):

```json
{"kind": "task", "task_id": "a1b2c3d4", "code": "print(42)", "timeout": 10}
```

Przykład wyniku (client → server):

```json
{"kind": "result", "task_id": "a1b2c3d4", "stdout": "42\n", "stderr": "", "exit_code": 0}
```
