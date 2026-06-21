# Frontend

Vue 3 single-page application with Vite.

## Setup

```bash
npm install
npm run dev
```

## Configuration

Set `VITE_API_URL` to point at the FastAPI backend (default: `http://localhost:8000`).

## Pages

- **LoginPage** — authentication
- **Dashboard** — send tasks, view history
- **AdminPage** — users, devices, provisioning, request chart
- **SnifferLogs** / **SnifferLogDetail** — packet sniffer logs (admin)

See [frontend documentation](../docs/documentation/docs/frontend.md) for details.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
