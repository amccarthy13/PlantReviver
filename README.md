# PlantReviver

A plant-watering tracker for iOS, backed by a dedicated async Python API.

- Track plants with watering intervals, last/next watered dates, and notes
- Offline-first: the app works fully offline and syncs when reconnected
- Planned premium tier: AI plant identification + weather/season-aware watering

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for the full design and decisions.

## Monorepo layout

```
backend/          FastAPI (async) API — see backend/README.md
infra/terraform/  Infrastructure-as-Code (Render + Cloudflare) — see infra/terraform/README.md
ios/              SwiftUI + SwiftData app — see ios/README.md
```

## Quick start (backend)

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
curl localhost:8000/healthz   # {"status":"ok"}
```
