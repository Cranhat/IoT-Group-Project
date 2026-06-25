# IoT Group Project

Projekt grupowy z Politechniki Wrocławskiej. Celem jest zbudowanie sieci IoT do bezpiecznej wymiany informacji między urządzeniami brzegowymi, z panelem webowym do zarządzania i monitorowania ruchu.

## Zespół

| Osoba | Rola |
|-------|------|
| Cyprian Burdzy (Cranhat) | Technical Leader |
| Nicole Jarczewska (Naitomi) | Developer |
| Natalia Kułak (Natomkul) | Developer |
| Oleh Marushchak | Developer |
| Tomek Piaseczny | Developer |

## Stos technologiczny

| Warstwa | Technologia |
|---------|-------------|
| Frontend | Vue 3, Vite |
| Backend API | Python, FastAPI, Uvicorn |
| Baza danych | PostgreSQL 16 |
| Agent provisioning | FastAPI, Docker API |
| Komunikacja urządzeń | TCP + TLS (mTLS), protokół JSON |
| Sniffer pakietów | Python, Scapy |
| Infrastruktura | Docker Compose |
| CI | GitHub Actions, pytest |
| Dokumentacja | MkDocs, PlantUML |

## Architektura (skrót)

```
Frontend (Vue) ──HTTP──► Backend (FastAPI) ──► PostgreSQL
                              │
                              ├──► Agent ──Docker──► Client containers
                              │
                              └──► Sniffer logs ◄── Packet sniffers

Client ◄──TLS──► Server   (zdalne wykonywanie kodu Python)
```

Szczegóły: [Architecture](architecture.md), [Docker](docker.md).

## Szybki start (Docker)

```bash
cp .env.example .env
# Uzupełnij POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB w pliku .env
docker compose up --build
```

Domyślne adresy (po uruchomieniu):

| Serwis | URL / port |
|--------|------------|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Agent | http://localhost:9000 |
| Server (TLS) | localhost:5000 |

Przy pierwszym uruchomieniu backend tworzy domyślnego administratora: `admin` / `1234`.

## Główne funkcje

- **Logowanie użytkowników** — panel webowy z podziałem na użytkownika i administratora.
- **Zadania** — wysyłanie kodu Python z dashboardu (zapis w bazie, przypisanie do urządzenia online).
- **Zarządzanie urządzeniami** — CRUD w panelu admina, provisioning kontenerów Docker przez agenta.
- **Komunikacja TLS** — serwer i klient wymieniają zadania przez szyfrowany kanał.
- **Sniffer pakietów** — monitorowanie ruchu TCP na portach backendu i serwera, podgląd logów w UI.

## Struktura repozytorium

```
IoT-Group-Project/
├── backend/           # FastAPI + warstwa bazy danych
│   ├── api/           # Endpointy REST
│   └── database/      # Inicjalizacja tabel, testy DB
├── frontend/          # Aplikacja Vue 3 (SPA)
├── server/            # Serwer TLS — wysyłanie zadań do klienta
├── client/            # Klient urządzenia — wykonywanie kodu Python
├── agent/             # Provisioning urządzeń jako kontenerów Docker
├── packet_sniffer/    # Przechwytywanie pakietów (Scapy)
├── communication/     # Generowanie certyfikatów TLS (CA, server, client)
├── docs/documentation/# Źródła MkDocs
├── docker-compose.yaml
└── README.md
```

## Dokumentacja

| Sekcja | Opis |
|--------|------|
| [Architecture](architecture.md) | Przepływy danych i komponenty |
| [Docker](docker.md) | Serwisy Compose, zmienne środowiskowe |
| [Backend](backend.md) | API, baza danych, endpointy |
| [Frontend](frontend.md) | Vue, komponenty, konfiguracja |
| [Communication](communication.md) | Server, client, agent, sniffer |
| [Tests](tests.md) | Uruchamianie testów |
| [CICD](cicd.md) | Pipeline GitHub Actions |
| [Contribution](contribution.md) | Zasady współpracy |

Dokumentacja jest generowana przez MkDocs (`mkdocs.yml` w `docs/documentation/`).
