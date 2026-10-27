# AGENTS.md

Guidance for AI coding agents working in this repository. The full project plan lives in `cpp-coding-platform-plan.md` — read the relevant section before starting a task, and update the plan if a decision changes.

## Project

A free, self-hostable CodingBat-style practice site for **C++ function-style exercises**. Multi-week group project and full-stack learning exercise. Build a real, usable app; add features deliberately.

## Architecture

> Thin frontend, server-owned application logic, isolated code execution.

```text
web/ (Next.js, React, TS, Monaco)
   -> GraphQL ->
backend/ (FastAPI, Python, GraphQL)
   -> backend/runner/ (Python package, in-process call) ->
Docker sandbox (backend/sandbox/) -> g++ + C++ test harness
```

| Dir | Responsibility |
|---|---|
| `web/` | UI, Monaco state, loading/error states, rendering results, `localStorage` |
| `backend/` | GraphQL API, validation, exercise metadata/content, calls the runner, maps runner results to GraphQL |
| `backend/runner/` | Temp workspaces, Docker run, limits, output capping, JSONL parsing, cleanup (orchestrates Docker only; never compiles or runs C++ on the host) |
| `backend/sandbox/` | Sandbox image (`Dockerfile`) and in-container `run.sh` (g++ compile + run with timeouts) |
| `exercises/` | Section folders (`01-basics/`), each holding exercise folders with `exercise.md`, `starter.cpp`, `tests.cpp` (hidden) |
| `docs/` | `architecture.md`, `development.md`, `execution-security.md` |

(The monorepo may not be scaffolded yet; check what exists before assuming.)

## Hard rules

- **Never compile or run student C++ in the Next.js or FastAPI process.** Untrusted code is compiled and run only inside the Docker sandbox; the backend's `runner` package merely launches and monitors that container.
- **Hidden tests never reach the browser.** The client sends only `exerciseId` and `code`.
- The frontend must not know about `g++`, Docker, resource limits, exit-code interpretation, workspaces, or hidden test locations.
- GraphQL resolvers call `runner.run_cpp(...)` directly (no separate execution service, no HTTP hop). The runner uses blocking `subprocess` calls, so run it off the event loop (sync resolver / `run_in_threadpool`).
- Docker sandbox: network disabled, non-root, ~0.5–1 CPU, ~128–256 MB, limited processes, read-only root FS with a small tmpfs `/tmp`, all capabilities dropped, exec timeout ~2–5s, compile timeout ~5–10s, one container per submission, **never** privileged, **never** expose the Docker socket, always clean up temp resources.
- Do not describe Docker as production-grade hostile-code security.
- Centralize `localStorage` access in `web/lib/storage/` (`codeStorage.ts`, `progressStorage.ts`); keys prefixed `cpp-platform:`. Handle storage being cleared or unavailable. Never store secrets or hidden tests.
- An exercise is **solved only when all hidden tests pass**.

## Result contract

Top-level statuses: `passed`, `failed`, `compilation_error`, `timeout`, `execution_error`.

Harness emits JSON Lines, one per test: `{"name","passed","expected","actual"}`. The harness, runner, GraphQL schema, and frontend must agree on this shape — if you change it, update all four layers and the docs together. The runner's internal `Stage`/`timed_out`/`exit_code` fields are not part of this contract; the backend maps them to the top-level statuses above.

## Exercise conventions

- One self-contained directory per exercise, inside exactly one section folder, e.g. `exercises/01-basics/001-sum/`.
- Function-style: learner implements a function, not a full program.
- Use **sections** (Basics, Conditionals, Loops, …), not difficulty levels or tags. A section is the parent folder; every exercise has exactly one. Free navigation, no required order.
- No metadata file. The exercise `id` is its folder name (`001-sum`), unique across the whole repo, and is the only identifier (no separate slug). Section name/order come from the section folder name (`01-basics`); the title is the first `# Heading` in `exercise.md`. Never store these values a second time.
- The backend builds an `id -> path` index by scanning `exercises/*/*/`; never build a filesystem path from a client-supplied `exerciseId`.
- Harness is a small custom C++ one; tests continue after a failure and report each independently.

## Stack and tooling

- Frontend: Next.js App Router, React, TypeScript, Monaco. npm.
- Backend: Python 3.11+ (runner uses `StrEnum`), FastAPI, GraphQL (library chosen at implementation), venv + pip/`requirements.txt`.
- Runner: pure-stdlib Python package in `backend/runner/`; shells out to the Docker CLI. No Node.js service.
- Dev environment: Windows + WSL2 (Ubuntu) + Docker Desktop. Prefer POSIX shell commands for project scripts.
- Don't install a separate Docker Engine in WSL when using Docker Desktop integration.

## Scope discipline (do not overbuild)

Out of scope until the core works: authentication, user profiles, databases, server-side progress, submission history, leaderboards, multiple languages, queues/workers, advanced sandboxing, admin dashboard. Keep the GraphQL schema minimal (`sections` with their exercises, `exercise(id)`, `executeCode(exerciseId, code)`) and grow it only for real features. Don't optimize deployment before local works.

## Workflow

- Follow the roadmap phases in the plan (env -> Docker C++ [done: `backend/runner`] -> harness -> runner integration -> FastAPI/GraphQL -> frontend -> persistence -> hardening -> deploy). Don't start the frontend before the execution path is proven.
- Keep changes focused; avoid commits that mix unrelated architectural areas.
- Add tests alongside changes: frontend (rendering, section grouping, reset, storage, loading/error), backend (queries, validation, mutation, runner failures), runner (compile ok/fail, pass/fail, timeout, runtime error, malformed output, output cap, cleanup; Docker-dependent tests marked so they can be skipped without Docker), plus integration tests across layers.
- Branch per feature (`feature/...`); PRs include a description, screenshots for UI changes, tests, and notes on API/schema/setup changes.
- Update `README.md` and `docs/` when setup, architecture, or the execution contract changes.
- Distinguish error types in the UI (network/API, compile, timeout, runtime, test failure) rather than a generic "something went wrong."

## Before finishing a task

1. Does it respect the hard rules above?
2. Are tests added/updated and passing?
3. Are docs and the cross-layer result contract still consistent?
4. Did I avoid adding scope beyond what was asked?
