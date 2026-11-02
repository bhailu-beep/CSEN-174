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
5. Open http://localhost:3000. Click **Try Demo Account** on the login page (or log in as `student` / `Demo123!`), or sign up with any username.

Press `Ctrl + C` in the terminal to stop it.

## Other commands

| Command |
|---|---|
| `npm test` | Runs the automated tests (25 tests in `tests/`) |
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
| `/profile` | Stats, progress by topic, reset progress |

## Placeholders until the backend is ready

- `src/lib/runCode.ts`: Run Code shows **sample** results; code is not actually compiled.
- `src/lib/exercises.ts` and `src/lib/lessons.ts`: the 24 exercises and 8 lessons are written in the frontend for now.
- `src/lib/auth.ts`: login is saved in the browser only and is **not secure**.

