# Development setup

Dev environment: Windows + Docker Desktop (WSL2 optional). Docker Desktop must be running for `/run`.

## 1. Database (PostgreSQL in Docker)

```bash
docker ps --filter name=completec-db     # should say "Up"
docker start completec-db                # only if it exists but is stopped
```

First time (or to recreate it):

```bash
docker run -d --name completec-db --restart unless-stopped -p 5432:5432 \
  -e POSTGRES_USER=completec -e POSTGRES_PASSWORD=completec -e POSTGRES_DB=completec postgres:16-alpine
docker exec -i completec-db psql -U completec -d completec < backend/setup.sql
```

**Existing databases** must run this once (it fails if two usernames differ only by case):

```sql
CREATE UNIQUE INDEX users_username_lower_key ON users (LOWER(username));
```

## 2. Backend

```bash
cd backend
python -m venv .venv                 # first time
.venv/Scripts/activate               # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt      # first time
uvicorn main:app --reload --port 8000
```

Needs `backend/.env` (database URL, JWT secret). API docs: http://localhost:8000/docs.
The first `/run` builds the sandbox image (about 50 s); later runs take about 4 s.
CORS allows `http://localhost:3000` with credentials.

## 3. Frontend

```bash
cd frontend
cp .env.example .env.local           # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install                          # first time
npm run dev                          # http://localhost:3000
```

## Tests

```bash
python -m pytest -q                  # from the repo root: backend
cd frontend && npm test              # frontend (fetch is mocked)
```

## Auth in short

- `/auth/register` and `/auth/login` return an access token (15 min) and set an httpOnly refresh cookie (7 days, path `/auth`).
- The frontend keeps the access token in memory, refreshes it once on a 401, and calls `/auth/refresh` on page load to restore a session.
- Exercise tests are public by design (`GET .../tests`); `/run` returns the expected value for each test.
