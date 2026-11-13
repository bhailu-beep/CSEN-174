# AGENTS.md

Guidance for AI coding agents working in this repository. The full project plan lives in `cpp-coding-platform-plan.md` — read the relevant section before starting a task, and update the plan if a decision changes.

## Project

A free, self-hostable CodingBat-style practice site for **C++ function-style exercises**. Multi-week group project and full-stack learning exercise. Build a real, usable app; add features deliberately.

## Architecture

> Thin frontend, server-owned application logic, isolated code execution.

```text
web/ (Next.js, React, TS, Monaco)
   -> HTTP JSON ->
backend/ (FastAPI, Python)
   -> backend/runner/ (Python package, in-process call) ->
Docker sandbox (backend/sandbox/) -> g++ + C++ test harness
```

| Dir | Responsibility |
|---|---|
| `web/` | UI, Monaco state, loading/error states, rendering results, `localStorage` |
| `backend/` | HTTP API, validation, exercise metadata/content, calls the runner, maps runner results to JSON |
| `backend/runner/` | Temp workspaces, Docker run, limits, output capping, JSONL parsing, cleanup (orchestrates Docker only; never compiles or runs C++ on the host) |
| `backend/sandbox/` | Sandbox image (`Dockerfile`), in-container `run.sh` (g++ compile + run with timeouts), and the shared C++ test harness `harness.h` (`check`, `to_str`, `json_escape`) |
| `exercises/` | Lesson folders (`basics/`), each holding exercise folders (`sum/`) with `tester.cpp` and `tests.txt` only. Problem text, hints, and starter code live in the frontend |
| `docs/` | `architecture.md`, `development.md`, `execution-security.md` |

(The monorepo may not be scaffolded yet; check what exists before assuming.)

## Hard rules

- **Never compile or run student C++ in the Next.js or FastAPI process.** Untrusted code is compiled and run only inside the Docker sandbox; the backend's `runner` package merely launches and monitors that container.
- **The client never sends tests or expected answers.** It sends the lesson id, the exercise id, and `code`; the backend owns the tests and does the scoring. Tests are not secret, because this is a learning platform: `GET /lessons/{lessonId}/exercises/{exerciseId}/tests` is public (the tests are not user-specific, so it needs no login), and `/run` returns the expected value for each test.
- The frontend must not know about `g++`, Docker, resource limits, exit-code interpretation, workspaces, or where test files live on disk.
- Route handlers call `runner.run_cpp(...)` directly (no separate execution service, no HTTP hop). The runner uses blocking `subprocess` calls, so run it off the event loop (sync handler / `run_in_threadpool`).
- Docker sandbox: network disabled, non-root, ~0.5–1 CPU, ~128–256 MB, limited processes, read-only root FS with a small tmpfs `/tmp`, all capabilities dropped, exec timeout ~2–5s, compile timeout ~5–10s, one container per submission, **never** privileged, **never** expose the Docker socket, always clean up temp resources.
- Do not describe Docker as production-grade hostile-code security.
- Centralize `localStorage` access in `web/lib/storage/` (`codeStorage.ts`, `progressStorage.ts`); keys prefixed `cpp-platform:`. Handle storage being cleared or unavailable. Never store secrets.
- An exercise is **solved only when all tests pass**.

## Result contract

Top-level statuses: `passed`, `failed`, `compilation_error`, `timeout`, `execution_error`.

The sandbox prints one JSON line per test, `{"actual"}`, in test order. Python compares those with the exercise's `TestCase` objects and produces `{"passed","expected","actual"}`. The runner, HTTP API, and frontend agree on that scored shape — if you change it, update those layers and the docs together. The runner's internal `Stage`/`timed_out`/`exit_code` fields are not part of this contract; the backend maps them to the top-level statuses above.

## Exercise conventions

- One self-contained directory per exercise, inside exactly one lesson folder, e.g. `exercises/basics/sum/`.
- Function-style: learner implements a function, not a full program.
- Use **lessons** (Basics, Conditionals, Loops, …), not difficulty levels or tags. A lesson is the parent folder; every exercise has exactly one. Free navigation, no required order.
- No metadata file and no numeric ids. The lesson id and the exercise id are the folder slugs (`basics`, `sum`). An exercise id is unique within its lesson, and the exercise is identified by that pair. A new exercise is a new folder; nothing else is renumbered. Descriptions, examples, hints, and starter code live in the frontend, not in `exercises/`.
- The backend builds a `(lesson id, exercise id) -> path` index by scanning `exercises/*/*/`; never build a filesystem path from a client-supplied id. Each folder holds only `tester.cpp` and `tests.txt`.
- `tester.cpp` includes the student's `solution.cpp`, calls that function once per case, and `report`s the actual return value. `main` returns 0 after every case so a wrong answer is distinguishable from a crash. `tests.txt` is parsed into test objects (`inputs`, `expected`). Expected answers are stripped before the file is mounted into the sandbox.

## Stack and tooling

- Frontend: Next.js App Router, React, TypeScript, Monaco. npm.
- Backend: Python 3.11+ (runner uses `StrEnum`), FastAPI, venv + pip/`requirements.txt`. JSON routes, the same style as `backend/routers/auth.py`.
- Runner: pure-stdlib Python package in `backend/runner/`; shells out to the Docker CLI. No Node.js service.
- Dev environment: Windows + WSL2 (Ubuntu) + Docker Desktop. Prefer POSIX shell commands for project scripts.
- Don't install a separate Docker Engine in WSL when using Docker Desktop integration.

## Scope discipline (do not overbuild)

Out of scope until the core works: authentication, user profiles, databases, server-side progress, submission history, leaderboards, multiple languages, queues/workers, advanced sandboxing, admin dashboard. Keep the HTTP API minimal (`GET /lessons`, `GET /lessons/{lessonId}/exercises/{exerciseId}`, `POST /lessons/{lessonId}/exercises/{exerciseId}/run`) and grow it only for real features. Don't optimize deployment before local works.

## Workflow

- Follow the roadmap phases in the plan (env -> Docker C++ [done: `backend/runner`] -> harness -> runner integration -> FastAPI routes -> frontend -> persistence -> hardening -> deploy). Don't start the frontend before the execution path is proven.
- Keep changes focused; avoid commits that mix unrelated architectural areas.
- Add tests alongside changes: frontend (rendering, lesson grouping, reset, storage, loading/error), backend (routes, validation, run requests, runner failures), runner (compile ok/fail, pass/fail, timeout, runtime error, malformed output, output cap, cleanup; Docker-dependent tests marked so they can be skipped without Docker), plus integration tests across layers.
- Branch per feature (`feature/...`); PRs include a description, screenshots for UI changes, tests, and notes on API/schema/setup changes.
- Update `README.md` and `docs/` when setup, architecture, or the execution contract changes.
- Distinguish error types in the UI (network/API, compile, timeout, runtime, test failure) rather than a generic "something went wrong."

## Before finishing a task

1. Does it respect the hard rules above?
2. Are tests added/updated and passing?
3. Are docs and the cross-layer result contract still consistent?
4. Did I avoid adding scope beyond what was asked?
