# CompleteC Frontend

The website for **CompleteC**, a C++ practice platform for SCU students. Built with Next.js, React and TypeScript.

## Run it (VS Code)

You need **Node.js 20 or newer** (check with `node --version`).

1. In VS Code: **File → Open Folder…** and pick this folder (or double-click `completec-frontend.code-workspace`).
2. Open the terminal: **Terminal → New Terminal**.
3. Install packages (first time only):
   ```bash
   npm install
   ```
4. Start the site:
   ```bash
   npm run dev
   ```
5. Open http://localhost:3000 and sign up. The backend must be running (see `docs/development.md`).

Press `Ctrl + C` in the terminal to stop it.

## Other commands

| Command |
|---|---|
| `npm test` | Runs the automated tests in `tests/` (`fetch` is mocked, no backend needed) |
| `npm run build` | Checks everything compiles, like the real deployment would |
| `npm start` | Runs the built version (after `npm run build`) |

## Pages

| URL | What it is |
|---|---|
| `/` | Home page |
| `/signup`, `/login` | Username + password (no email) |
| `/dashboard` | Overall progress, the **Full C++** section, and the 8 topic cards |
| `/topics/<topic>` | A quick lesson, then the exercises for one topic, e.g. `/topics/loops` |
| `/topics/all` | **Full C++**: every exercise, with search, topic filters, and a random pick |
| `/exercises/<slug>` | Problem, examples, hint, Monaco editor, test results |
| `/profile` | Stats and progress by topic |

## What lives where

- The **backend** owns accounts, tests and scoring, saved code, and progress. `src/lib/api.ts` is the only place that calls it.
- `src/lib/exercises.ts`, `src/lib/lessons.ts`: problem text, hints, starter code and lessons live in the frontend.
- `.env.local` sets `NEXT_PUBLIC_API_URL` (copy `.env.example`).
