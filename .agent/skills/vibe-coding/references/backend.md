# Backend — Django Ninja, Hexagonal (Ports & Adapters)

The whole point of Hexagonal: **business logic depends on abstractions, never on Django, the ORM, Redis, MinIO, or HTTP.** Those are details that plug in at the edges. If you can't unit-test a use case without booting Django, the boundaries are wrong.

## Layers (dependency points inward only)

```
HTTP / CLI / jobs ──▶ [driving adapter] ──▶ Use case ──▶ Port ◀── [driven adapter] ──▶ DB / Redis / MinIO
   (Django Ninja)                          (application)  (interface)   (ORM / cache / storage)
                                                │
                                                ▼
                                            Domain (pure)
```

- **Domain** — entities, value objects, domain services, invariants. Zero imports of Django, Ninja, ORM, pydantic-from-ninja, redis, minio. Plain Python.
- **Application (use cases)** — orchestrates domain + driven ports to fulfill one intent. Depends on port *interfaces*, never concrete adapters.
- **Ports** — interfaces (`typing.Protocol` or ABC).
  - *Driving ports*: the use cases the outside world invokes.
  - *Driven ports*: what the app needs from infrastructure (repositories, cache, storage, token service, clock, id generator, mailer…).
- **Adapters** — concrete implementations at the edges.
  - *Driving adapter*: **Django Ninja routers** (also: management commands, Celery tasks).
  - *Driven adapters*: Django ORM repository, Redis cache, MinIO/FS storage, JWT token service.

## Folder layout

Organize by bounded context, then by layer inside it:

```
src/
├── <context>/                 # e.g. accounts, billing, courses
│   ├── domain/
│   │   ├── entities.py        # pure dataclasses / objects + invariants
│   │   └── value_objects.py
│   ├── application/
│   │   ├── ports.py           # driven port Protocols (repos, cache, storage, auth...)
│   │   └── use_cases.py       # one class/function per intent
│   └── adapters/
│       ├── api.py             # Django Ninja router (driving adapter) — THIN
│       ├── schemas.py         # Ninja request/response schemas (NOT domain types)
│       ├── repositories.py    # ORM repository implementing the repo port
│       ├── models.py          # Django ORM models (infrastructure, not domain)
│       └── storage.py         # MinIO/FS adapter if this context stores files
├── shared/
│   ├── ports.py               # cross-context ports (Clock, IdGen, Mailer)
│   └── adapters/              # their implementations
├── config/                    # Django settings split (see Parity)
│   ├── settings/{base,dev,prod}.py
│   └── container.py           # wiring: bind ports → adapters per environment
└── manage.py
```

The **container** (`config/container.py`) is where ports are bound to adapters. Use cases receive their ports by constructor injection; the Ninja router builds the use case from the container. Don't `import` a concrete adapter inside a use case.

## Request flow (the only correct shape)

A router does three things: parse → call use case → serialize. Example skeleton:

```python
# adapters/api.py  (driving adapter — thin)
from ninja import Router
from .schemas import CreateCourseIn, CourseOut
from config.container import build_create_course
from ..application.use_cases import CourseAlreadyExists

router = Router(tags=["courses"])

@router.post("/", response={201: CourseOut, 409: dict}, auth=jwt_auth)
def create_course(request, payload: CreateCourseIn):
    use_case = build_create_course()          # ports wired in the container
    try:
        course = use_case(payload.to_command(), owner_id=request.auth.user_id)
        return 201, CourseOut.from_domain(course)
    except CourseAlreadyExists:
        return 409, {"detail": "course exists"}
```

```python
# application/ports.py  (driven port — an interface)
from typing import Protocol
from ..domain.entities import Course

class CourseRepository(Protocol):
    def get_by_slug(self, slug: str) -> Course | None: ...
    def add(self, course: Course) -> None: ...
```

```python
# application/use_cases.py  (pure orchestration, no Django)
from dataclasses import dataclass
from .ports import CourseRepository
from ..domain.entities import Course

class CourseAlreadyExists(Exception): ...

@dataclass
class CreateCourse:
    courses: CourseRepository
    def __call__(self, cmd, owner_id: str) -> Course:
        if self.courses.get_by_slug(cmd.slug):
            raise CourseAlreadyExists
        course = Course.create(slug=cmd.slug, title=cmd.title, owner_id=owner_id)
        self.courses.add(course)
        return course
```

```python
# adapters/repositories.py  (driven adapter — the only file that touches the ORM)
from ..application.ports import CourseRepository
from ..domain.entities import Course
from .models import CourseModel

class DjangoCourseRepository(CourseRepository):
    def get_by_slug(self, slug):
        row = CourseModel.objects.filter(slug=slug).first()
        return _to_domain(row) if row else None
    def add(self, course: Course) -> None:
        CourseModel.objects.create(**_to_row(course))
```

Key discipline: **Ninja `Schema`s and ORM `Model`s never leak past the adapter layer.** Map ORM rows ↔ domain entities in the repository; map domain entities ↔ Ninja schemas in `from_domain`/`to_command`. The domain knows neither.

## Dev/prod parity

One schema, two databases, two storage backends, swapped by config — never by branching inside logic.

- **DB:** SQLite in dev, Postgres in prod via the same Django models and migrations. Avoid SQLite-only or Postgres-only column tricks in shared code; if you need a Postgres feature (JSONB ops, full-text), gate it behind a repository method so the port stays clean. Always run migrations against Postgres before shipping.
- **Storage:** one `Storage` driven port; `MinioStorage` (prod) and `LocalFileStorage` (dev) implement it. Bind the right one in the container by env. Use cases call `storage.save(...)`, never `boto3`/`open()` directly.
- **Settings split:** `config/settings/{base,dev,prod}.py`. `dev` → SQLite + local FS + no Redis unless testing it; `prod` → Postgres + MinIO + Redis (if used). Select via `DJANGO_SETTINGS_MODULE`.
- **Secrets/config:** env vars only (`.env` in dev, Coolify env in prod). Same variable names both sides.

## Redis (opt-in)

Only add it for a real hot path. When you do: define a `Cache` driven port, implement `RedisCache` (prod) and a no-op/in-memory cache (dev/tests), and bind by env. Document key shape, TTL, and what write invalidates it. No Redis call ever appears inside a use case except through the port.

## Auth (JWT)

- A `TokenService` driven port: `issue(claims) -> str`, `verify(token) -> Claims`.
- JWT adapter implements it; a Ninja auth class (`jwt_auth`) verifies the bearer token and attaches claims to `request.auth`.
- Use cases receive the authenticated identity as a plain value (e.g. `owner_id`), not a Django `User`. Keep Django's auth model in the adapter layer.
- Provide access + refresh; refresh rotation lives in a use case, not the router.

## Packaging & commands (uv)

```bash
uv sync                      # install from pyproject/uv.lock
uv add django django-ninja   # add deps
uv run python manage.py migrate
uv run python manage.py runserver   # dev: native, NO docker
```

## Deploy (Docker Compose on Coolify)

- Dev runs natively (no Docker). Compose is for prod and prod-like local runs only.
- Compose services: `web` (gunicorn/uvicorn serving Django Ninja), `db` (Postgres), `minio`, and `redis` *only if used*. Run migrations as a release step before `web` starts.
- Coolify builds from the repo and injects env vars; keep the image env-agnostic and driven entirely by `DJANGO_SETTINGS_MODULE` + env vars.
- Health check endpoint on the API so Coolify can gate rollouts.

## Checklist before calling backend work done

- [ ] No Django/ORM/redis/minio import in `domain/` or `application/`.
- [ ] Every infrastructure touch goes through a driven port.
- [ ] Routers are thin (parse → use case → serialize); no business logic.
- [ ] Schemas and ORM models don't leak past adapters.
- [ ] dev (SQLite/FS) and prod (Postgres/MinIO) differ only by container binding.
- [ ] Migrations verified against Postgres.
- [ ] Redis present only with a documented reason.
