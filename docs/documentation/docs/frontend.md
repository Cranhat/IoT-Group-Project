# Frontend

Single-page application w **Vue 3** z bundlerem **Vite**.

## Uruchomienie lokalne

```bash
cd frontend
npm install
npm run dev
```

Aplikacja domyślnie dostępna pod http://localhost:5173.

## Konfiguracja

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `VITE_API_URL` | `http://localhost:8000` | Adres backendu FastAPI |

W Dockerze frontend łączy się z backendem przez sieć Compose. Ustaw `VITE_API_URL` w `.env`, jeśli backend jest na innym hoście.

## Struktura

```
frontend/src/
├── main.js              # Punkt wejścia Vue
├── App.vue              # Routing stanu (strony)
├── style.css
├── components/
│   ├── LoginPage.vue    # Logowanie
│   ├── Dashboard.vue    # Wysyłka zadań, historia
│   ├── AdminPage.vue    # Panel admina (użytkownicy, urządzenia, wykres)
│   ├── SnifferLogs.vue  # Lista logów sniffera
│   └── SnifferLogDetail.vue  # Szczegóły pojedynczego logu
└── assets/
```

## Strony aplikacji

Nawigacja odbywa się przez stan w `App.vue` (`currentPage`), bez Vue Router.

| Strona | Dostęp | Opis |
|--------|--------|------|
| Login | publiczny | Formularz logowania → `POST /login` |
| Dashboard | zalogowany | Wysyłka problemów, lista zadań |
| Admin Panel | `privilege_type === 'administrator'` | CRUD użytkowników i urządzeń, provisioning, wykres zadań |
| Sniffer Logs | admin | Podgląd przechwyconych pakietów |
| Log Detail | admin | Szczegóły wybranego logu |

## Integracja z API

Frontend komunikuje się z backendem przez `fetch`. Przykładowe endpointy:

- `POST /login` — logowanie
- `GET /tasks?user_id=` — zadania użytkownika
- `POST /tasks` — nowe zadanie
- `GET /devices`, `POST /add/devices`, `PUT /update/devices/{id}`, `DELETE /delete/devices/{id}`
- `POST /devices/provision` — provisioning przez agenta
- `GET /sniffer/logs` — logi sniffera
- `GET /tables/users`, `GET /tables/task_logs` — dane dla panelu admina

## Skrypty npm

| Polecenie | Opis |
|-----------|------|
| `npm run dev` | Serwer deweloperski Vite |
| `npm run build` | Build produkcyjny |
| `npm run preview` | Podgląd buildu |

## Docker

Kontener `iot_frontend` montuje kod źródłowy i uruchamia `npm run dev` z hot-reload. Port mapowany przez `HOST_PORT_FRONTEND` (domyślnie 5173).
