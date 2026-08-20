You are a senior software architect. Turn the **APP IDEA** below into a complete, build-ready technical plan grounded **strictly** in the fixed stack and architectures defined here. Do not propose alternative technologies, do not "suggest a better approach to the stack." If the idea genuinely cannot be expressed in this stack, say so explicitly and stop — otherwise commit fully.

Think first, then produce the plan. Where the idea is ambiguous, make a reasonable assumption, **state it inline**, and keep moving — do not stall asking questions. Collect any blocking unknowns into a single "Open Questions" section at the end.

---

## APP IDEA

```
SmartQueue is an intelligent virtual queue management system designed to eliminate physical waiting lines. It allows users to join a queue or book an appointment remotely via smartphone, track live status, receive arrival notifications, and minimize crowded waiting areas.

### Key System Features
* Remote Booking: Request a ticket or schedule an appointment from anywhere using a mobile device.
* Live Tracking: Real-time visibility into the current serving number and accurate remaining wait time.
* Smart Alerts: Automated push/SMS notifications sent to users before their turn arrives to prompt immediate travel to the location.
* Crowd Reduction: Eliminates overcrowding in waiting halls across medical, government, and commercial facilities.

### Common Use Cases
* Medical Clinics: Dental offices, specialized clinics, and hospitals.
* Government Offices: Public service centers for official paperwork and transactions.
```

---

## FIXED STACK (non-negotiable)

**Backend**
- Django + **Django Ninja** for the HTTP API
- **SQLite** in dev, **Postgres** in prod (same schema, parity required)
- **Docker Compose** for deploy + prod local runs; **no Docker** in dev (run natively)
- **Redis** for cache — *only if a concrete need is justified*, otherwise omit it
- **MinIO** for storage in prod, **local filesystem** storage in dev
- Architecture: **Hexagonal (Ports & Adapters)**
- Server: **Coolify**
- Auth: **JWT**
- Package manager: **uv**

**Frontend**
- **Next.js** (latest) + **shadcn** with **RTL** support
- **Zustand** for state
- **ApexCharts** for charts
- **GSAP** + **three.js** for animation / 3D where the idea calls for it
- **reactbits** for animated components
- Must deploy cleanly to **both Netlify and Vercel** (no vendor lock-in features)
- Architecture: **feature-based**, strict **DRY**
- Package manager: **npm**
- **React Compiler** is enabled

---

## ARCHITECTURE RULES TO ENFORCE

**Backend — Hexagonal**
- The **domain layer is pure**: entities, value objects, and domain logic with zero Django / ORM / framework imports.
- **Ports** are interfaces (Python `Protocol`/ABC). Split them:
  - *Driving ports* (use cases the outside world calls)
  - *Driven ports* (what the domain needs from infrastructure: repositories, cache, storage, auth, clock, etc.)
- **Adapters** implement driven ports and live at the edges:
  - Django ORM → repository adapter
  - Redis → cache adapter
  - MinIO / local FS → storage adapter (one port, two adapters, selected by env)
  - JWT → auth/token adapter
  - **Django Ninja → driving adapter** (HTTP), thin: it parses input, calls a use case, serializes output. No business logic in routers.
- Every infrastructure choice (SQLite↔Postgres, local FS↔MinIO) sits behind a port so dev/prod swap is config-only.

**Frontend — feature-based + DRY**
- Group by **feature**, not by file type. Each feature owns its components, hooks, Zustand store slice, API calls, and types.
- A clear shared layer (`shared/` or `lib/` + `components/ui` for shadcn) holds anything used by 2+ features. Nothing is copy-pasted across features.
- RTL is first-class: layout, direction, and component mirroring must work in `dir="rtl"`.
- Because **React Compiler is on**, do **not** hand-wrap things in `useMemo`/`useCallback`/`memo` for performance — let the compiler optimize. Only memoize when there's a correctness reason.
- Keep it deployable to Netlify **and** Vercel: stick to standard Next.js, avoid provider-exclusive APIs, and keep any edge/runtime assumptions portable.

---

## REQUIRED OUTPUT (in this order)

1. **Scope & restatement** — what's being built, in/out of scope, key assumptions.
2. **Domain model** — entities, value objects, aggregates, invariants. Framework-free.
3. **Use cases** — list the driving ports (application services) with their inputs/outputs.
4. **Ports & adapters map** — a table: each driven port → its adapter(s) → the concrete tech (ORM/Redis/MinIO/JWT/…). Note any dev-vs-prod adapter swaps.
5. **Data model** — tables/fields/relations, indexes, and any SQLite↔Postgres differences to watch.
6. **API surface** — Django Ninja routers and endpoints, request/response schemas, status codes, pagination, and where auth is required.
7. **Auth flow** — JWT issuance, refresh, storage, and how it's enforced (the auth port + Ninja dependency).
8. **Caching** — only if justified: what's cached, keys, invalidation, TTL. If not needed, state "no Redis required and why."
9. **Storage** — what gets stored, the storage port, MinIO (prod) vs local FS (dev) wiring, upload/download flow.
10. **Frontend feature breakdown** — list features; for each, its folder layout, components (shadcn/reactbits), Zustand store slice, and the API calls it consumes.
11. **Shared layer** — shared UI, hooks, utils, types — what's promoted to shared to satisfy DRY.
12. **Routing & data fetching** — Next.js route structure, server vs client components, where data is fetched, and RTL handling.
13. **Charts / animation / 3D** — only where the idea warrants: which features use ApexCharts / GSAP / three.js and for what.
14. **Deployment & config** — Docker Compose services for prod, Coolify notes, env var matrix (dev vs prod), and how the frontend stays Netlify+Vercel portable. Call out uv (backend) and npm (frontend) setup.
15. **Build sequence** — ordered milestones from domain → ports → adapters → API → frontend features → deploy, so it can be built incrementally.
16. **Open questions** — only genuine blockers.

## OUTPUT STYLE
- Be concrete and decision-dense. Prefer tables and tight lists over prose.
- **No application code** unless explicitly asked — interfaces, signatures, schemas, and folder trees are fine and encouraged.
- Respect dev/prod parity everywhere; never let an environment difference leak past a port.
