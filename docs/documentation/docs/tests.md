# Tests

Testy automatyczne oparte na **pytest**.

## Uruchomienie

```bash
pip install -r backend/requirements.txt
PYTHONPATH=backend:. python -m pytest
```

Na Windows:

```powershell
$env:PYTHONPATH="backend;."
python -m pytest
```

## Lokalizacja testów

| Katalog | Zakres |
|---------|--------|
| `backend/database/tests/` | Warstwa bazy: insert, fetch, update, inicjalizacja |
| `packet_sniffer/tests/` | Sniffer: zapis logów, przetwarzanie pakietów |

Przykładowe pliki:

- `test_database.py` — inicjalizacja tabel, seed admina
- `test_db_insert.py`, `test_db_fetch.py`, `test_db_update.py` — operacje CRUD
- `test_packet_sniffer.py` — logika sniffera (mocki HTTP)

## CI

Testy uruchamiane są automatycznie w GitHub Actions na Ubuntu i Windows z Pythonem 3.10–3.12. Szczegóły: [CICD](cicd.md).

## Mockowanie

W testach sniffera używane są mocki (`unittest.mock`) do izolacji wywołań HTTP do backendu.

Testy bazy danych wymagają działającej instancji PostgreSQL ze skonfigurowanymi zmiennymi `POSTGRES_*` (lub uruchomienia w Dockerze z dostępem do `db`).

## Pokrycie (obecny stan)

| Moduł | Testy |
|-------|-------|
| Backend API (FastAPI) | brak dedykowanych testów |
| Agent | brak |
| Server / Client | brak |
| Frontend | brak |

Nowa logika biznesowa powinna być pokrywana testami jednostkowymi w odpowiednim katalogu `tests/`.
