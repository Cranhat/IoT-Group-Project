# Contribution

## Pull requesty

Zmiany w repozytorium wprowadzamy przez **pull requesty**. Każdy PR wymaga zatwierdzenia co najmniej jednego członka zespołu oraz Technical Leadera.

## Format commit message

```
[Topic]
Why: [Why the change is being submitted]
What: [What are the changes]
```

Przykład:

```
[backend] Add sniffer log pagination
Why: Admin panel loads too many rows at once
What: Add limit/sort query params to GET /sniffer/logs
```

## Konwencje kodu

- **Python:** zgodność z istniejącym stylem modułów (`backend/`, `agent/`, `server/`, `client/`).
- **Frontend:** Vue 3 Composition API (`<script setup>`), spójny styl CSS w komponentach.
- **Testy:** nowa logika w backendzie/database — dodaj testy pytest w odpowiednim katalogu `tests/`.
- **Dokumentacja:** aktualizuj pliki w `docs/documentation/docs/` przy zmianach API lub architektury.

## Lokalne sprawdzenie przed PR

```bash
# Testy Python
pip install -r backend/requirements.txt
PYTHONPATH=backend:. python -m pytest

# Frontend (opcjonalnie)
cd frontend && npm install && npm run build

# Stack Docker (opcjonalnie)
docker compose up --build
```

## Gałęzie

Pracuj na osobnych branchach feature/fix. Nie commituj plików z `.env`, certyfikatów TLS ani kluczy prywatnych.
