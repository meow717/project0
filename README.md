# SmartQueue — Virtual Queue Management

Eliminate physical waiting lines. Join a queue or book an appointment remotely,
track live status and accurate remaining wait time, and receive a smart alert
before your turn. Built for medical clinics, government offices and commercial
venues — Arabic-first (RTL) with an ar/en toggle.

| | Backend | Frontend |
| --- | --- | --- |
| **Framework** | Django 6 + django-ninja | Next.js 16 (App Router) + React 19 |
| **Architecture** | Hexagonal (Ports & Adapters) | Feature-based + DRY |
| **State / Data** | Postgres (prod) / SQLite (dev), Redis cache | Zustand |
| **Auth** | JWT (PyJWT), roles: customer / staff / admin | JWT in persisted store |
| **UI / Viz** | — | shadcn (RTL), ApexCharts, GSAP, reactbits |
| **Packages** | uv | npm |
| **Deploy** | Docker Compose → Coolify | Vercel / Netlify |

## Features

- **Directory** — browse businesses (clinics, offices, venues) with live crowd
  level, now-serving number, waiting count and estimated wait per service.
- **Join queue** — issue a ticket remotely; track position + remaining wait live
  (5s polling). Walk-in tickets for staff.
- **Smart alerts** — in-app notification when your turn is approaching
  (threshold crossing on queue transitions); email/SMS channels pluggable via
  the notification port.
- **Appointments** — time-slot bookings with working-hours and overlap checks;
  staff confirm / complete / no-show.
- **Staff dashboard** — live queue board (call / start / complete / no-show),
  service management, business settings, and ApexCharts analytics (served per
  hour/day, by service, avg wait).
- **Notification center** — unread badge in the shell, mark read / all read.

## Repository layout

```
backend/    Django + ninja, hexagonal — src/accounts, src/businesses, src/queue,
            src/bookings, src/notifications; see backend/README.md and backend/AGENTS.md
frontend/   Next.js + shadcn, feature-based — features/browse, features/queue,
            features/booking, features/dashboard, features/notifications
ARCHITECTURE.md   layers, the dependency rule, and how to add a feature on each side
```

## Run it locally

**Backend** (SQLite, no Docker):

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo      # optional demo business + staff
uv run python manage.py runserver      # http://localhost:8000/api/docs
```

**Frontend** (in another terminal):

```bash
cd frontend
npm install
npm run dev                             # http://localhost:3000
```

Open <http://localhost:3000>, sign up, then create your own business from the
API (or log in as the demo staff `staff@demo.com` / `staffpass123` after
`seed_demo`). Toggle language (ar ⇄ en) and theme from the app top bar.

## Deploy

- **Backend → Coolify:** build from `backend/Dockerfile` (or
  `backend/docker-compose.yml`, which also brings up Postgres + Redis + MinIO).
  Fill `backend/.env.example` values in Coolify.
- **Frontend → Vercel/Netlify:** Vercel is zero-config; Netlify uses the
  included `netlify.toml`. Set `NEXT_PUBLIC_API_URL` to the deployed backend's
  `/api`.

## Verified

Backend: `uv run pytest` → 21 passing (auth, businesses, queue + wait estimator,
bookings, notifications; use-case + HTTP flows). `uv run ruff check .` clean.
Frontend: `npm run build` and `npm run lint` pass with the React Compiler enabled.
