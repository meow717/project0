---
name: vibe-coding
description: The house stack and conventions for building full-stack apps — a Hexagonal (Ports & Adapters) Django Ninja backend and a feature-based Next.js frontend. Use this skill WHENEVER building, scaffolding, planning, or extending an app in this stack, or whenever the work touches any of these — Django Ninja, Hexagonal / Ports-and-Adapters, SQLite-dev with Postgres-prod, MinIO storage, Redis cache, JWT auth, uv, Coolify, Docker Compose, or a Next.js + shadcn (RTL) + Zustand + ApexCharts + GSAP/three.js frontend with the React Compiler. Trigger it even when the request just says "add a feature", "build an API", "scaffold a page", or "wire up auth" in an existing project of this shape — it encodes the architecture rules, dev/prod parity, and folder conventions the agent must follow so output matches the house style instead of generic defaults.
---

# Vibe Coding — House Stack & Conventions

This skill encodes how we build. Follow it so the output matches our architecture, our dev/prod parity, and our folder conventions — not a generic tutorial layout. Two architectures govern everything:

- **Backend → Hexagonal (Ports & Adapters).** Domain logic is pure; framework and infrastructure live at the edges behind ports. Read `references/backend.md`.
- **Frontend → feature-based + strict DRY.** Group by feature, promote anything shared, never copy-paste across features. Read `references/frontend.md`.

Read the relevant reference file **before** writing code for that side. The body below is the always-true core: the stack, the global rules, and the build order.

## The fixed stack

| Concern | Backend | Frontend |
|---|---|---|
| Framework | Django + **Django Ninja** API | **Next.js** (latest) |
| Architecture | **Hexagonal (Ports & Adapters)** | **Feature-based**, strict **DRY** |
| State / data | Postgres (prod) / SQLite (dev) | **Zustand** |
| UI | — | **shadcn** with **RTL** support |
| Charts | — | **ApexCharts** |
| Animation / 3D | — | **GSAP** + **three.js** (only when needed) |
| Components | — | **reactbits** (animated) |
| Cache | **Redis** — *only if justified* | — |
| Storage | **MinIO** (prod) / local FS (dev) | — |
| Auth | **JWT** | consumes JWT |
| Packages | **uv** | **npm** |
| Compiler | — | **React Compiler** enabled |
| Deploy | **Docker Compose** on **Coolify** | **Netlify or Vercel** (both must work) |
| Dev runtime | run **natively, no Docker** | `npm run dev` |

This stack is locked. Do not substitute technologies. If an idea genuinely can't be expressed in it, say so explicitly rather than swapping a tool.

## Global rules (apply on both sides)

1. **Dev/prod parity is sacred.** SQLite↔Postgres, local FS↔MinIO, no-Docker-dev↔Compose-prod. Every environment difference hides behind config or a port — never behind an `if env == "prod"` scattered through business logic. Code must not know or care which side it's on.
2. **Redis is opt-in.** Don't add caching by default. Add it only when there's a concrete, named hot path, and document what's cached, the key, the TTL, and the invalidation trigger. If it isn't needed, say so.
3. **RTL is first-class, not a polish pass.** Plan layout, direction, and component mirroring for `dir="rtl"` from the start. Use logical CSS properties (`margin-inline-start`, not `margin-left`).
4. **The React Compiler optimizes for you.** Do **not** hand-wrap things in `useMemo` / `useCallback` / `React.memo` for performance — that fights the compiler. Memoize only for correctness (stable identity an effect depends on).
5. **Stay portable across Netlify and Vercel.** Use standard Next.js only; avoid provider-exclusive APIs and keep edge/runtime assumptions portable.
6. **Right package manager per side.** `uv` for backend, `npm` for frontend. Never mix.

## Build order

Build inward-out on the backend, then outward on the frontend:

1. **Domain** — entities, value objects, invariants. Pure, no Django imports.
2. **Ports** — driving ports (use cases) and driven ports (repositories, cache, storage, auth, clock) as `Protocol`/ABC interfaces.
3. **Adapters** — ORM repository, Redis cache, MinIO/FS storage, JWT auth. One port can have a dev and a prod adapter selected by config.
4. **API** — thin Django Ninja routers that parse input, call a use case, serialize output. No logic in routers.
5. **Frontend features** — one folder per feature (components + hooks + Zustand slice + api calls + types); promote shared pieces.
6. **Deploy** — Docker Compose for the backend on Coolify; keep the frontend deployable to both Netlify and Vercel.

Each step is independently testable before the next. See the reference files for concrete folder layouts, request-flow skeletons, and the per-tool conventions.

## When to read what

- Anything backend (API, model, auth, storage, cache, domain logic, deploy) → **`references/backend.md`**
- Anything frontend (pages, components, state, charts, animation, styling, deploy) → **`references/frontend.md`**

Both reference files are short and pattern-dense. Read the whole relevant one — don't skim a single heading.
