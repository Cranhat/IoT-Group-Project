# Backend

REST API w Pythonie (FastAPI) z warstwą dostępu do PostgreSQL.

## Uruchomienie lokalne

```bash
cd backend/database
python -m venv venv
source venv/bin/activate   # Linux
pip install -r ../requirements.txt

# Ustaw zmienne POSTGRES_* i DB_HOST=localhost
uvicorn api.app:app --reload --app-dir ../
```

W Dockerze backend startuje automatycznie jako `iot_fastapi`.

## Struktura

```
backend/
├── api/
│   ├── app.py        # Aplikacja FastAPI, CORS, startup
│   ├── users.py      # CRUD użytkowników
│   ├── tasks.py      # Zadania użytkowników
│   ├── devices.py    # CRUD urządzeń
│   ├── agent.py      # Proxy do agenta (provisioning)
│   ├── sniffer.py    # Odczyt logów sniffera
│   └── tables.py     # Generyczny dostęp do tabel
└── database/
    └── src/
        ├── database.py   # Połączenie, inicjalizacja tabel
        ├── db_init.py    # DDL tabel
        ├── db_fetch.py
        ├── db_insert.py
        ├── db_update.py
        └── objects.py    # Modele Pydantic
```

## Baza danych

Tabele tworzone przy starcie (`initializeTables`):

| Tabela | Opis |
|--------|------|
| `users` | Użytkownicy (`name`, `privilege_type`) |
| `passwords` | Hasła powiązane z `user_id` |
| `devices` | Urządzenia IoT (`status`, `ip_address`, `container_name`, `device_name`) |
| `task_logs` | Zadania wysłane z dashboardu |
| `task_result_logs` | Wyniki wykonania zadań |
| `http_logs` | Logi żądań HTTP |
| `packet_sniffer_logs` | Przechwycone payloady TCP |

Domyślny administrator (gdy baza pusta): `admin` / `1234`.

## Endpointy API

### Autoryzacja

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `POST` | `/login` | Logowanie (`username`, `passcode`) |

### Użytkownicy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/users` | Lista użytkowników |
| `POST` | `/add/users` | Dodaj użytkownika |
| `DELETE` | `/delete/users/{user_id}` | Usuń użytkownika |

### Zadania

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/tasks?user_id=` | Zadania użytkownika |
| `POST` | `/tasks` | Utwórz zadanie (`user_id`, `problem`) |

### Urządzenia

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/devices` | Lista urządzeń |
| `POST` | `/add/devices` | Dodaj urządzenie |
| `PUT` | `/update/devices/{device_id}` | Aktualizuj urządzenie |
| `DELETE` | `/delete/devices/{device_id}` | Usuń urządzenie (+ kontener przez agenta) |

### Agent (proxy)

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `POST` | `/devices/provision` | Provisionuj urządzenie Docker |
| `GET` | `/devices/provision/{container_name}/status` | Status provisioningu |
| `DELETE` | `/devices/provision/{container_name}` | Deprovisionuj urządzenie |

### Sniffer

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/sniffer/logs?limit=&sort=&port=` | Logi pakietów |

### Tabele (generyczne)

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/tables/{table}` | Odczyt tabeli |
| `POST` | `/tables/{table}` | Wstaw wiersz |
| `PUT` | `/tables/{table}/{id}` | Aktualizuj wiersz |

Dozwolone tabele: `users`, `passwords`, `devices`, `task_logs`, `task_result_logs`, `http_logs`, `packet_sniffer_logs`.

## Zależności

Plik `backend/requirements.txt`: FastAPI, Uvicorn, psycopg2-binary, httpx, pydantic, pytest, scapy.
