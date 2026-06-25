# CI/CD

Pipeline CI uruchamiany jest przez **GitHub Actions** przy każdym push i pull request.

Plik: `.github/workflows/ci.yml`

## Job: Tests

| Parametr | Wartość |
|----------|---------|
| Trigger | `push`, `pull_request` |
| OS | `ubuntu-latest`, `windows-latest` |
| Python | 3.10, 3.11, 3.12 |
| Strategia | matrix (`fail-fast: false`) |

## Kroki pipeline

1. **Checkout** — pobranie kodu (`actions/checkout@v3`).
2. **Set up Python** — instalacja wersji z macierzy (`actions/setup-python@v4`).
3. **Install dependencies** — `pip install -r backend/requirements.txt`.
4. **Run tests** — `python -m pytest` z ustawionym `PYTHONPATH`:
   - Unix: `backend:workspace_root`
   - Windows: `backend;workspace_root`

## Co testuje CI

Obecnie pipeline uruchamia testy pytest z katalogów:

- `backend/database/tests/`
- `packet_sniffer/tests/`

CI **nie** uruchamia automatycznie:

- testów integracyjnych Docker Compose,
- buildu frontendu,
- linterów.

## Rozszerzenie pipeline (propozycja)

Przy dodawaniu nowych jobów warto rozważyć:

- `npm run build` w `frontend/`,
- testy z wymaganiem uruchomionej bazy (service container PostgreSQL),
- publikację dokumentacji MkDocs na GitHub Pages po merge do `main`.
