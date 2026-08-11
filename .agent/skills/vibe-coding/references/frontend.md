# Frontend — Next.js, feature-based + strict DRY

Group by **feature**, not by file type. A feature owns everything it needs; anything used by two or more features is promoted to a shared layer. The test for DRY here isn't "no duplication ever" — it's "no *meaningful* logic or UI copy-pasted between features."

## Folder layout

```
src/
├── app/                       # Next.js routes ONLY — thin, compose features
│   └── (routes)/.../page.tsx  # imports from features/, almost no logic
├── features/
│   └── <feature>/             # e.g. courses, auth, dashboard
│       ├── components/        # UI specific to this feature
│       ├── hooks/             # feature hooks (data, behavior)
│       ├── store.ts           # this feature's Zustand slice
│       ├── api.ts             # calls to the backend for this feature
│       ├── types.ts
│       └── index.ts           # public surface of the feature (barrel)
├── shared/
│   ├── components/ui/         # shadcn components (generated)
│   ├── components/            # cross-feature composite components
│   ├── hooks/                 # cross-feature hooks
│   ├── lib/                   # api client, utils, formatters, jwt handling
│   └── types/
└── styles/
```

Rules:
- **`app/` is plumbing.** A `page.tsx` wires layout + pulls a feature's exported component. No data logic, no fetching sprawl, no business rules in routes.
- **Features don't import each other's internals.** Cross-feature reuse goes through `shared/`. If feature A needs something from feature B, the shared piece moves to `shared/`.
- **Promote on the second use.** First use: keep it local. Second feature needs it: move to `shared/` and import in both. That's how DRY is enforced without premature abstraction.

## State (Zustand)

- One **slice per feature** in `features/<f>/store.ts`. Keep slices small and feature-scoped.
- Compose into a root store only if features genuinely share live state; otherwise keep independent stores — they're cheap.
- Selectors: subscribe to the narrowest slice a component needs (`useStore(s => s.x)`) so re-renders stay tight.
- Server data (fetched from the API) generally doesn't belong in Zustand long-term; keep Zustand for UI/client state and ephemeral session state. Fetch server data in the feature's `api.ts`/hooks and cache at the data-fetching layer.
- JWT: store/refresh tokens in `shared/lib` (one auth module), expose `useAuth` from there — never re-implement token logic per feature.

## React Compiler is ON — memoization rules

- Do **not** add `useMemo` / `useCallback` / `React.memo` for performance. The compiler handles memoization; hand-wrapping fights it and adds noise.
- Only reach for them when **correctness** needs a stable identity (e.g. a value in a dependency array that must not change). Even then, prefer restructuring.
- Write straightforward components and let the compiler optimize. Reviewers should flag manual perf-memoization as a smell.

## shadcn + RTL (first-class)

- Set direction at the root (`<html dir="rtl">` or a direction provider) and design every component to mirror correctly.
- Use **logical CSS properties** everywhere: `margin-inline-start` / `padding-inline-end` / `inset-inline`, not `left`/`right`. Tailwind logical utilities (`ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`) over `ml-`/`mr-`.
- Icons/chevrons that imply direction must flip under RTL.
- Test every screen in RTL before considering it done — it's a layout requirement, not a finishing touch.
- shadcn components live in `shared/components/ui`; wrap (don't fork) them when a feature needs a variant.

## Server vs client components

- Default to **Server Components**; mark `"use client"` only where you need interactivity, Zustand, browser APIs, GSAP/three.js, or ApexCharts.
- Fetch data in Server Components or feature hooks; pass plain data down. Keep client bundles lean.
- Charts and animation libraries are client-only — isolate them in small client components so they don't pull whole pages client-side.

## Charts, animation, 3D, components

- **ApexCharts** for all charts. Wrap in a client component; load dynamically (`next/dynamic`, `ssr: false`) since it needs the DOM. Centralize theme/colors in `shared/` so charts stay consistent and RTL-aware.
- **GSAP** for animation, **three.js** for 3D — only when the feature actually calls for it. Keep them in dedicated client components; clean up timelines/contexts on unmount.
- **reactbits** for ready-made animated components — reach for these before hand-rolling animations.
- Don't pull in animation/3D weight on routes that don't use it.

## Backend contract

- The backend is Django Ninja with JWT. Each feature's `api.ts` calls its endpoints through the shared API client in `shared/lib` (one client: base URL from env, attaches the bearer token, handles refresh).
- Types in `features/<f>/types.ts` mirror the Ninja response schemas. Keep one source of truth per response shape.

## Packaging & deploy

- **npm** only.
- Must build and run identically on **Netlify and Vercel**:
  - Standard Next.js only — no Vercel-exclusive or Netlify-exclusive APIs.
  - Don't assume a specific edge runtime; keep middleware/runtime config portable.
  - All config via env vars with the same names on both platforms (`NEXT_PUBLIC_API_URL`, etc.).
  - Verify a production build (`npm run build`) passes cleanly before shipping.
- `npm run dev` for local development.

## Checklist before calling frontend work done

- [ ] Code is grouped by feature; `app/` routes are thin.
- [ ] No feature imports another feature's internals; shared code is in `shared/`.
- [ ] No manual `useMemo`/`useCallback`/`memo` added for performance.
- [ ] Every screen verified in RTL with logical properties.
- [ ] Zustand slices are feature-scoped; server data isn't dumped into global state.
- [ ] Charts/animation isolated in client components, loaded only where used.
- [ ] One shared API client handles base URL + JWT; types mirror Ninja schemas.
- [ ] `npm run build` passes and uses no provider-exclusive features.
