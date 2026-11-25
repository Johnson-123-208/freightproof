# FreightProof (Demo MVP)

**Every freight charge. Verified with evidence.**

Lean monorepo demo for AI-assisted freight invoice auditing. Monetary discrepancy checks are **deterministic** (Python `Decimal` arithmetic only — no LLM for money math). The UI surfaces findings with contract citations and a dispute-letter draft.

## Structure

```
freightproof/
├── web/          # Vite + React + TypeScript + Tailwind (port 5178)
├── backend/      # FastAPI + SQLAlchemy (port 8006)
├── .env.example
└── deploy.txt    # gitignored local deploy template
```

## Quick start

### API (port 8006)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8006
```

On startup the app creates SQLite tables and seeds:

- Contract **CFL-MASTER-2024** — Dallas TX → Chicago IL @ $2.45/mi
- Invoice **FLT-2024-88421** billed **$2,150** vs expected **~$1,874.25** → **overcharge** finding

- Health: `http://127.0.0.1:8006/health`
- Docs: `http://127.0.0.1:8006/docs`

### Web (port 5178)

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5178`. Vite proxies `/api` and `/health` to the API.

### Production build

```bash
cd web && npm install && npm run build
```

## API routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/api/v1/invoices` | List invoices |
| POST | `/api/v1/invoices` | Add invoice |
| POST | `/api/v1/invoices/{id}/audit` | Run deterministic audit |
| GET | `/api/v1/invoices/{id}/audits` | Audit history |
| POST | `/api/v1/audits/{id}/dispute-letter` | Dispute draft |
| GET | `/api/v1/contracts/rates` | Contract rate table |

## Environment

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | No | Default SQLite `backend/freightproof.db` |
| `CORS_ORIGINS` | No | Default includes `localhost:5178` |
| `SUPABASE_URL` / `SUPABASE_KEY` | No | Reserved for future Postgres |
| `VITE_API_URL` | No | Set in production if API is on another host |

Copy `.env.example` to `.env` at repo root and/or `backend/` as needed.

## Deploy sketches

- **web/vercel.json** — SPA rewrites; point `YOUR_RENDER_API_HOST` to the Render API.
- **backend/render.yaml** — Python web service running `uvicorn`.

## License

MIT