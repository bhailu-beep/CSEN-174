# AGENTS.md

Guidance for AI coding agents working in this repository. The full project plan lives in `cpp-coding-platform-plan.md` — read the relevant section before starting a task, and update the plan if a decision changes.

## Project

A free, self-hostable CodingBat-style practice site for **C++ function-style exercises**. Multi-week group project and full-stack learning exercise. Build a real, usable app; add features deliberately.

## Architecture

> Thin frontend, server-owned application logic, isolated code execution.

```text
web/ (Next.js, React, TS, Monaco)
   -> GraphQL ->
backend/ (Flask, Python, GraphQL)
   -> internal HTTP POST /execute ->
executor/ (Node.js, TS)
   -> Docker sandbox -> g++ + C++ test harness
```

| Dir | Responsibility |
|---|---|
| `web/` | UI, Monaco state, loading/error states, rendering results, `localStorage` |
| `backend/` | GraphQL API, validation, exercise metadata/content, calls the executor, maps executor results to GraphQL |
| `executor/` | Temp workspaces, compile, Docker run, limits, JSONL parsing, cleanup |
| `exercises/` | Per-exercise `exercise.md`, `starter.cpp`, `tests.cpp` (hidden) |
| `docker/` | Container configs (e.g. `cpp-runner`) |
| `docs/` | `architecture.md`, `development.md`, `execution-security.md` |

(The monorepo may not be scaffolded yet; check what exists before assuming.)

## Hard rules

- **Never run student C++ in the Next.js or Flask process.** Only the executor + Docker runs untrusted code.
- **Hidden tests never reach the browser.** The client sends only `exerciseId` and `code`.
- The frontend must not know about `g++`, Docker, resource limits, exit-code interpretation, workspaces, or hidden test locations.
- Flask does not execute C++; it calls the executor over plain HTTP (no GraphQL between Flask and executor).
- Docker sandbox: network disabled, non-root, ~1 CPU, ~128–256 MB, limited processes, exec timeout ~2–5s, compile timeout ~5–10s, one container per submission, **never** privileged, **never** expose the Docker socket, always clean up temp resources.
- Do not describe Docker as production-grade hostile-code security.
- Centralize `localStorage` access in `web/lib/storage/` (`codeStorage.ts`, `progressStorage.ts`); keys prefixed `cpp-platform:`. Handle storage being cleared or unavailable. Never store secrets or hidden tests.
- An exercise is **solved only when all hidden tests pass**.

## Result contract

Top-level statuses: `passed`, `failed`, `compilation_error`, `timeout`, `execution_error`.

Harness emits JSON Lines, one per test: `{"name","passed","expected","actual"}`. The harness, executor, GraphQL schema, and frontend must agree on this shape — if you change it, update all four layers and the docs together.

## Exercise conventions

- One self-contained directory per exercise, e.g. `exercises/001-sum/`.
- Function-style: learner implements a function, not a full program.
- Use **tags** (arrays, strings, loops, recursion, math, pointers, …), not difficulty levels. Free navigation, no required order.
- Avoid duplicating metadata (id, slug, title, tags) across places.
- Harness is a small custom C++ one; tests continue after a failure and report each independently.

## Stack and tooling

- Frontend: Next.js App Router, React, TypeScript, Monaco. npm.
- Backend: Python, Flask, GraphQL (library chosen at implementation), venv + pip/`requirements.txt`.
- Executor: Node.js, TypeScript, npm.
- Dev environment: Windows + WSL2 (Ubuntu) + Docker Desktop. Prefer POSIX shell commands for project scripts.
- Don't install a separate Docker Engine in WSL when using Docker Desktop integration.

## Scope discipline (do not overbuild)

Out of scope until the core works: authentication, user profiles, databases, server-side progress, submission history, leaderboards, multiple languages, queues/workers, advanced sandboxing, admin dashboard. Keep the GraphQL schema minimal (`exercises`, `exercise(slug)`, `tags`, `executeCode(exerciseId, code)`) and grow it only for real features. Don't optimize deployment before local works.

## Workflow

- Follow the roadmap phases in the plan (env -> Docker C++ -> harness -> executor -> Flask/GraphQL -> frontend -> persistence -> hardening -> deploy). Don't start the frontend before the execution path is proven.
- Keep changes focused; avoid commits that mix unrelated architectural areas.
- Add tests alongside changes: frontend (rendering, filtering, reset, storage, loading/error), backend (queries, validation, mutation, executor failures), executor (compile ok/fail, pass/fail, timeout, runtime error, malformed output, cleanup), plus integration tests across layers.
- Branch per feature (`feature/...`); PRs include a description, screenshots for UI changes, tests, and notes on API/schema/setup changes.
- Update `README.md` and `docs/` when setup, architecture, or the execution contract changes.
- Distinguish error types in the UI (network/API, compile, timeout, runtime, test failure) rather than a generic "something went wrong."

## Before finishing a task

1. Does it respect the hard rules above?
2. Are tests added/updated and passing?
3. Are docs and the cross-layer result contract still consistent?
4. Did I avoid adding scope beyond what was asked?
