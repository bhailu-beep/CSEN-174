# C++ Coding Practice Platform — Project Plan

## 1. Project Overview

Build a free, potentially self-hostable coding-practice website inspired by CodingBat, starting with **C++ function-style exercises**.

The project is intended to:
- provide a practical coding-practice experience;
- serve as a full-stack portfolio/project experience;
- teach full-stack development through hands-on implementation;
- give the team experience working across frontend, backend, APIs, containers, and code execution;
- be substantial enough to develop over multiple weeks as a group project;
- keep the architecture understandable and modular rather than prematurely optimizing for a huge production platform;
- leave room for accounts, persistent progress, additional languages, and stronger execution infrastructure later.

The initial version should be a **real, usable application**, not just a proof of concept. At the same time, features should be added deliberately so the team does not spend the entire project building infrastructure before users can actually solve exercises.

---

## 2. Core User Experience

A learner should be able to:

1. Open the exercise list.
2. Browse or filter exercises using tags.
3. Choose any exercise without following a required sequence.
4. Read the exercise description and examples.
5. Edit starter C++ code in an in-browser Monaco editor.
6. Run the code against hidden tests.
7. See clear execution feedback, including:
   - individual test results;
   - expected vs. actual output where appropriate;
   - compilation errors;
   - timeout errors;
   - execution errors.
8. Have their current code saved locally in the browser.
9. See an exercise marked **solved only when all hidden tests pass**.
10. Reset their code to the original starter code.
11. Reset their locally stored progress.
12. Return to exercises they have already worked on.

The application should feel like a small but complete coding-practice platform rather than a collection of disconnected technical demos.

---

## 3. Project Scope

Because this is a **multi-week group project**, the scope can be larger than a bare-minimum MVP. The goal is to build a solid first release while keeping some major platform features explicitly post-MVP.

### Core Release

The first substantial release should include:

- C++ exercises
- Function-style exercise interface
- Exercise list
- Exercise pages
- Exercise descriptions written in Markdown
- Examples and starter code
- Exercise tags
- Tag-based filtering/search or browsing
- Monaco code editor
- Run button
- Hidden tests
- Custom lightweight C++ test harness
- JSON Lines (JSONL) test output
- C++ compilation and execution in Docker
- Node.js + TypeScript execution service
- Flask + GraphQL application backend
- Detailed test results
- Compilation errors
- Timeout handling
- Execution errors
- Browser `localStorage` for:
  - current code per exercise;
  - locally solved exercises;
- Reset starter code
- Reset local progress
- Free navigation between exercises
- Basic responsive layout
- Basic loading/error states
- Automated tests for important frontend/backend/executor behavior
- Documentation for local setup and architecture

### Good Stretch Features for the Multi-Week Project

These are reasonable additions if the core experience is working reliably:

- Exercise search by title/tag
- More sophisticated exercise filtering
- Exercise categories
- Better test-result visualization
- Code editor settings such as font size/theme
- Keyboard shortcuts
- Run-state indicators
- Confirmation before resetting modified code
- Exercise completion/progress summary stored locally
- Recently attempted exercises stored locally
- More robust validation of submitted code
- Rate limiting on the execution endpoint
- Better execution logging
- Admin/developer workflow for adding exercises
- More comprehensive integration tests
- Deployment of the complete application
- Basic monitoring/logging for the deployed services
- Improved accessibility

### Explicitly Post-MVP / Future Work

Do not let these features block the initial release:

- Authentication
- User profiles
- PostgreSQL/database-backed user data
- Server-side persistent progress
- Submission history
- Leaderboards
- Social features
- Multiple programming languages
- Advanced analytics
- Queues/workers for large-scale execution
- Production-grade hostile-code sandboxing
- Sophisticated collaborative features
- Full administrator dashboard

These features can be added after the team has a working application and a stable execution pipeline.

---

## 4. Product Decisions

### Exercise style

Use function-style exercises.

Example:

```cpp
int sum(int a, int b) {
    // Your code here
}
```

The learner implements the function rather than writing an entire program.

This makes exercises easier to present consistently and lets the platform control the test harness.

### Navigation

Learners can jump between exercises freely. There is no required progression.

### Difficulty

Do not make difficulty levels a core organizational concept for now.

Use tags instead, such as:

- arrays
- strings
- loops
- conditionals
- recursion
- math
- pointers
- structs/classes

Additional tags can be added as the exercise collection grows.

### Run vs. Submit

The primary action is **Run**.

A separate Submit workflow can be added later if the team decides that a distinction between experimenting and completing an exercise is useful.

### Solved status

An exercise becomes locally solved only when **all hidden tests pass**.

A partial pass does not count as solved.

Solved state is stored in `localStorage`, so it is not authoritative and can be manually altered or lost if browser data is cleared. That is acceptable until accounts/server-side persistence are introduced.

### Local code persistence

`localStorage` is appropriate for the MVP because it is being used for convenience rather than security or authoritative data.

It can store:
- the user's current code for each exercise;
- solved exercise IDs;
- optional lightweight UI preferences.

It should **not** store:
- passwords;
- authentication tokens/secrets;
- hidden tests;
- authoritative user records;
- anything that must remain secure.

The UI should gracefully handle the possibility that local storage has been cleared or is unavailable.

### Reset behavior

Provide a way to reset an exercise to its original starter code.

If the user has modified the code, consider displaying a confirmation before replacing it.

Also provide a separate way to reset locally tracked progress.

---

## 5. Architecture

The main architectural principle is:

> **Thin frontend, server-owned application logic, isolated code execution.**

The project has three major application layers:

```text
Frontend
Next.js / React / TypeScript
        |
        | GraphQL
        v
Application Backend
Flask / Python / GraphQL
        |
        | HTTP
        v
Execution Service
Node.js / TypeScript
        |
        v
Docker sandbox
        |
        v
g++ + C++ test harness
```

Each layer should have a narrow responsibility.

### Frontend

The frontend should primarily handle:
- rendering the exercise UI;
- Monaco editor state;
- user interactions;
- loading/error states;
- displaying execution results;
- reading/writing `localStorage`.

The frontend should **not** know:
- how `g++` is invoked;
- how Docker is started;
- where hidden tests live;
- how resource limits are enforced;
- how compiler exit codes are interpreted;
- how execution workspaces are created;
- how student code is sandboxed.

### Flask application backend

Flask is the application's main backend/API layer.

Responsibilities include:
- exposing the GraphQL API;
- validating application-level requests;
- serving exercise metadata/content to the frontend;
- coordinating execution requests;
- calling the Node execution service;
- converting executor results into the GraphQL response model;
- providing a future home for authentication, users, progress, submissions, etc.

The Flask backend should not directly execute arbitrary C++ code.

### GraphQL

GraphQL is the primary API between the Next.js frontend and Flask.

The initial schema can expose concepts such as:

```graphql
query {
  exercises {
    id
    slug
    title
    tags
  }
}
```

```graphql
query {
  exercise(slug: "001-sum") {
    title
    description
    starterCode
    tags
  }
}
```

And an execution mutation such as:

```graphql
mutation {
  executeCode(
    exerciseId: "001-sum"
    code: "int sum(int a, int b) { return a + b; }"
  ) {
    status
    tests {
      name
      passed
      expected
      actual
    }
  }
}
```

The exact schema should be designed as implementation begins rather than trying to predict every future feature now.

### Node.js + TypeScript executor

The executor is intentionally separated from Flask.

Responsibilities include:
- receiving execution requests from Flask;
- locating the exercise's hidden test files;
- creating a temporary workspace;
- compiling the student's C++ code;
- starting the Docker sandbox;
- enforcing execution constraints;
- collecting stdout/stderr/exit codes;
- parsing JSONL test output;
- returning structured results;
- cleaning up temporary resources.

The executor can use a simple internal HTTP endpoint such as:

```text
POST /execute
```

GraphQL does **not** need to be used between Flask and the executor. GraphQL is the application-facing API; a small internal HTTP interface is enough for the execution service.

### Why keep Node.js in the architecture?

The project uses Flask because Python is a useful backend framework for the team, while Node.js + TypeScript remains a useful technology to learn for the execution service.

Keeping the Node service narrow prevents the architecture from becoming unnecessarily complicated. Node is responsible for execution infrastructure; Flask is responsible for application/API logic.

---

## 6. Technology Stack

### Frontend / Web

- Next.js
- React
- TypeScript
- Next.js App Router
- Monaco Editor

### Application Backend

- Python
- Flask
- GraphQL
- A Python GraphQL library selected during implementation

### Execution Service

- Node.js
- TypeScript
- Internal HTTP API
- `g++`

### Isolation

- Docker
- WSL2 + Ubuntu for local development on Windows

### Exercise Content

- Markdown
- C++ source files
- Git repository storage

### Local Persistence

- Browser `localStorage`

### Package / Dependency Management

- npm for JavaScript/TypeScript
- Python virtual environment + pip/requirements for Flask initially
- Docker for execution environment

### Repository

- Monorepo

---

## 7. Repository Structure

A reasonable starting point is:

```text
coding-platform/
├── web/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── exercises/
│   │   │   └── [slug]/
│   │   │       └── page.tsx
│   │   └── ...
│   ├── components/
│   │   ├── CodeEditor.tsx
│   │   ├── ExerciseView.tsx
│   │   ├── ExerciseList.tsx
│   │   ├── RunButton.tsx
│   │   └── TestResults.tsx
│   ├── lib/
│   │   ├── graphql/
│   │   ├── exercises/
│   │   └── storage/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── graphql/
│   │   ├── exercises/
│   │   ├── services/
│   │   └── ...
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── executor/
│   ├── src/
│   │   ├── server.ts
│   │   ├── docker.ts
│   │   ├── compiler.ts
│   │   ├── tests.ts
│   │   └── workspace.ts
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
│
├── exercises/
│   ├── 001-sum/
│   │   ├── exercise.md
│   │   ├── starter.cpp
│   │   └── tests.cpp
│   ├── 002-...
│   └── ...
│
├── docker/
│   └── cpp-runner/
│       └── Dockerfile
│
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── execution-security.md
│
├── package.json
└── README.md
```

The exact folder names can change as implementation progresses. The important separation is:

```text
web/       -> frontend
backend/   -> Flask + GraphQL
executor/  -> Node + TypeScript + Docker execution
exercises/ -> exercise definitions and hidden tests
docker/    -> container configuration
docs/      -> project documentation
```

---

## 8. Exercise Format

Each exercise should be self-contained.

Example:

```text
exercises/
└── 001-sum/
    ├── exercise.md
    ├── starter.cpp
    └── tests.cpp
```

### `exercise.md`

```markdown
# Sum

Write a function that returns the sum of two integers.

## Examples

`sum(2, 3)` → `5`

`sum(-1, 5)` → `4`
```

### `starter.cpp`

```cpp
int sum(int a, int b) {
    // Your code here
}
```

### Hidden tests

`tests.cpp` should remain on the server/executor side.

The browser should never receive hidden tests as part of a normal exercise request.

As the exercise collection grows, each exercise can also have metadata such as:

```text
id
slug
title
tags
```

The team should avoid duplicating metadata in multiple places unnecessarily.

---

## 9. C++ Test Harness

The project should use a small custom C++ test harness rather than a large testing framework for the initial version.

### Goals

The harness should:
- call the student's function;
- test multiple inputs;
- report each test independently;
- continue after an individual test fails;
- produce machine-readable output;
- make it easy to create new exercises.

### JSONL output

Use **JSON Lines (JSONL)** so the executor can parse results line-by-line.

Example:

```text
{"name":"sum(2, 3)","passed":true,"expected":"5","actual":"5"}
{"name":"sum(-1, 5)","passed":false,"expected":"4","actual":"-6"}
```

The exact JSON schema should be standardized early so that the C++ harness, Node executor, Flask GraphQL layer, and frontend all agree on the result format.

### Result model

A failed exercise might eventually become:

```json
{
  "status": "failed",
  "tests": [
    {
      "name": "sum(2, 3)",
      "expected": "5",
      "actual": "5",
      "passed": true
    },
    {
      "name": "sum(-1, 5)",
      "expected": "4",
      "actual": "-6",
      "passed": false
    }
  ]
}
```

Compilation failure:

```json
{
  "status": "compilation_error",
  "compilerOutput": "..."
}
```

Timeout:

```json
{
  "status": "timeout"
}
```

Suggested top-level statuses:

- `passed`
- `failed`
- `compilation_error`
- `timeout`
- `execution_error`

---

## 10. Execution Service Design

The execution path should look approximately like this:

```text
User clicks Run
       |
       v
Next.js sends GraphQL mutation
       |
       v
Flask resolver
       |
       v
Node executor /execute
       |
       v
Create temporary workspace
       |
       v
Write student code + test files
       |
       v
Compile
       |
       +---- compilation failure -> return compiler output
       |
       v
Start Docker sandbox
       |
       v
Run compiled program
       |
       +---- timeout -> return timeout
       |
       +---- runtime failure -> return execution error
       |
       v
Parse JSONL
       |
       v
Return structured result
       |
       v
Flask GraphQL response
       |
       v
Next.js displays results
```

### Temporary workspace

Each submission should use an isolated temporary workspace, for example:

```text
/tmp/run-abc123/
```

The workspace should be cleaned up after execution whether the submission succeeds or fails.

### Important rule

Never execute arbitrary student C++ directly inside the normal Next.js process or Flask process.

The execution service and Docker layer exist specifically to separate untrusted code from the application itself.

---

## 11. Docker Sandbox

For the initial implementation, Docker provides a practical isolation boundary for C++ execution.

Suggested starting constraints:

| Restriction | Initial target |
|---|---|
| Network | disabled |
| User | non-root |
| CPU | ~1 CPU |
| Memory | ~128–256 MB |
| Process count | limited |
| Execution timeout | ~2–5 sec |
| Compilation timeout | ~5–10 sec |
| Filesystem | temporary isolated workspace |
| Container lifetime | one per submission |
| Privileged mode | never |
| Docker socket | never exposed to student code |
| Cleanup | always remove temporary resources |

These are starting values, not final production security guarantees.

### Compile and execution limits

Treat compilation and execution separately.

Compilation can receive a somewhat longer timeout than program execution because `g++` itself takes time.

### Security mindset

Student C++ should be treated as **untrusted input**.

The initial sandbox should prevent obvious problems such as:
- network access;
- unlimited CPU use;
- unlimited memory use;
- runaway processes;
- writing arbitrary host files;
- privileged container access.

Docker is useful isolation, but a Docker container by itself should not be described as a complete production-grade security solution for hostile arbitrary code.

If the platform eventually has significant public usage, stronger isolation, dedicated execution hosts, rate limiting, monitoring, and potentially a more specialized sandbox architecture should be considered.

---

## 12. GraphQL API Design

The GraphQL API should initially stay small.

### Exercise queries

Potential operations:

```text
exercises
exercise(slug)
tags
```

The exercise list response should contain enough metadata for browsing without sending unnecessary full exercise content for every item.

A single exercise query can return:

```text
title
description
starterCode
tags
```

### Execution mutation

Potential operation:

```text
executeCode(exerciseId, code)
```

The client sends:
- exercise identifier;
- student's current code.

The client should **not** send hidden tests.

### Future GraphQL additions

Once authentication/database support is introduced, GraphQL could also expose:

```text
user
progress
submissions
favorites
```

These should not be added simply because GraphQL makes them possible.

---

## 13. Frontend Structure

The main exercise page will likely contain:

```text
---------------------------------------------------
| Exercise title / tags                            |
---------------------------------------------------
| Description              | C++ Editor            |
| Examples                 |                       |
|                          |                       |
|                          |                       |
|                          |                       |
---------------------------------------------------
| Run                         Reset                |
---------------------------------------------------
| Results / compiler output / test details         |
---------------------------------------------------
```

### Components

Potential components:

- `ExerciseList`
- `ExerciseCard`
- `TagFilter`
- `ExerciseView`
- `ExerciseDescription`
- `CodeEditor`
- `RunButton`
- `ResetButton`
- `TestResults`
- `CompilationError`
- `ExecutionError`
- `LoadingState`

The exact component breakdown should be determined as the UI is built rather than over-designing it in advance.

### Monaco

Monaco is a good fit because it provides a real editor experience and can be configured for C++ syntax highlighting.

The frontend should treat the editor as a UI component; compilation remains entirely server-side.

---

## 14. Local Storage Design

A simple key structure can be used, for example:

```text
cpp-platform:code:<exercise-id>
cpp-platform:solved
cpp-platform:preferences
```

Example solved state:

```json
["001-sum", "002-max", "003-count-vowels"]
```

The implementation should centralize localStorage access rather than calling `localStorage` throughout random components.

For example:

```text
web/lib/storage/
    codeStorage.ts
    progressStorage.ts
```

This makes the storage implementation easier to replace later if progress moves to the server/database.

---

## 15. Error Handling

The application should distinguish different failure types rather than presenting every failure as "something went wrong."

### Frontend/API failures

Examples:
- network unavailable;
- GraphQL request failure;
- executor unavailable;
- malformed response.

### Compilation failure

Show the compiler output in a readable form.

### Timeout

Explain that the program exceeded the execution limit.

### Execution failure

Show useful runtime information where safe and appropriate.

### Test failure

Show:
- test name;
- expected result;
- actual result;
- pass/fail state.

### Successful execution

Show a clear indication that all tests passed.

---

## 16. Testing Strategy

Because this is a group project with several layers, testing should be introduced throughout development rather than left until the final week.

### Frontend tests

Test important behavior such as:
- exercise rendering;
- tag filtering;
- editor reset behavior;
- localStorage persistence;
- solved-state display;
- loading/error states.

### Flask/GraphQL tests

Test:
- exercise queries;
- exercise lookup;
- input validation;
- execution mutation behavior;
- conversion of executor results into GraphQL responses;
- handling of executor failures.

### Executor tests

Test:
- valid C++ compilation;
- failed compilation;
- passing tests;
- failing tests;
- timeout;
- runtime errors;
- malformed harness output;
- cleanup after success/failure.

### Integration tests

Eventually test the full path:

```text
GraphQL request
    -> Flask
    -> Node executor
    -> Docker
    -> C++ tests
    -> executor result
    -> GraphQL response
```

This is especially important because individual services can work correctly while their interfaces disagree.

---

## 17. Development Environment

The intended local development environment is:

```text
Windows
  |
  v
WSL2
  |
  v
Ubuntu
  |
  +---- Node.js / npm
  +---- Python / Flask
  +---- g++
  +---- Git
  +---- Docker CLI
          |
          v
      Docker Desktop
```

### Step 1 — Install WSL2

From PowerShell running as Administrator:

```powershell
wsl --install
```

Restart Windows when prompted.

Open Ubuntu and complete the initial Linux username/password setup.

Verify:

```powershell
wsl -l -v
```

The Ubuntu distribution should use **WSL 2**.

### Step 2 — Install Docker Desktop

Install Docker Desktop for Windows and use its WSL2 integration.

Enable integration for the Ubuntu distribution.

If using Docker Desktop + WSL2 integration, do **not** also install a separate Docker Engine inside Ubuntu unless there is a specific reason to do so.

Verify from Ubuntu:

```bash
docker --version
docker run hello-world
```

### Step 3 — Check Node.js

From Ubuntu:

```bash
node --version
npm --version
```

If Node is already installed and suitable for the project, there is no reason to reinstall it immediately.

### Step 4 — Check other tools

```bash
g++ --version
git --version
python3 --version
```

The goal of this phase is simply to make sure the development environment is ready before application development begins.

---

## 18. Development Roadmap

The project should be developed in stages so that each stage produces something testable.

### Phase 0 — Environment and repository setup

Goals:
- WSL2 working;
- Ubuntu working;
- Docker Desktop working with WSL2;
- Node/npm working;
- Python working;
- g++ working;
- Git working;
- monorepo created;
- basic README and team workflow established.

Deliverable:

```text
A shared repository that every team member can clone and run locally.
```

---

### Phase 1 — Prove C++ execution in Docker

Before building the web application, prove the hardest infrastructure concept.

Start with:

```text
hello.cpp
   -> Docker
   -> g++
   -> executable
   -> output
```

Learn:
- Docker images;
- containers;
- mounted files/workspaces;
- container cleanup;
- network disabling;
- resource limits;
- exit codes;
- timeouts.

Deliverable:

```text
A repeatable command/script that safely compiles and runs a simple C++ program in Docker.
```

---

### Phase 2 — Build the C++ test harness

Create the first real exercise:

```text
001-sum/
```

Implement:
- starter code;
- tests;
- JSONL output;
- passing tests;
- failing tests.

Deliverable:

```text
Student C++ code -> test harness -> JSONL results
```

---

### Phase 3 — Build the Node.js executor

Turn the manual Docker process into a service.

Implement:
- HTTP endpoint;
- request validation;
- temporary workspaces;
- compilation;
- Docker execution;
- timeouts;
- result parsing;
- cleanup.

Example request:

```json
{
  "exerciseId": "001-sum",
  "code": "int sum(int a, int b) { return a + b; }"
}
```

Deliverable:

```text
HTTP request -> Node executor -> Docker -> structured JSON result
```

---

### Phase 4 — Build Flask + GraphQL backend

Create the application backend around the executor.

Implement:
- Flask application;
- GraphQL schema;
- exercise queries;
- exercise lookup;
- `executeCode` mutation;
- communication with Node executor;
- backend tests.

Deliverable:

```text
GraphQL request -> Flask -> Node executor -> GraphQL response
```

At this point, the complete backend path should work even without a polished frontend.

---

### Phase 5 — Build the Next.js frontend

Implement the learner-facing experience:

1. exercise list;
2. exercise page;
3. Markdown description;
4. examples;
5. Monaco editor;
6. Run button;
7. loading state;
8. test results;
9. compiler errors;
10. timeout/runtime errors;
11. reset button.

Deliverable:

```text
A user can open the website, write C++, run it, and understand the result.
```

---

### Phase 6 — Local persistence and exercise discovery

Add:
- localStorage code persistence;
- solved state;
- reset starter code;
- reset progress;
- exercise tags;
- tag filtering;
- more exercises.

Deliverable:

```text
A useful coding-practice site rather than a single-exercise demo.
```

---

### Phase 7 — Quality and hardening

Test difficult cases:
- correct code;
- incorrect code;
- compiler errors;
- infinite loops;
- timeouts;
- memory-heavy programs;
- large output;
- malformed requests;
- malformed harness output;
- simultaneous runs;
- executor unavailable;
- Docker failures;
- cleanup after failed executions;
- attempts to access the network;
- attempts to create excessive processes/files.

Improve:
- validation;
- error messages;
- logging;
- cleanup;
- test coverage;
- accessibility;
- UI polish.

---

### Phase 8 — Deployment

A likely deployment architecture is:

```text
                 ┌─────────────────────┐
                 │      Browser        │
                 └──────────┬──────────┘
                            │
                            v
                 ┌─────────────────────┐
                 │ Next.js / Vercel    │
                 └──────────┬──────────┘
                            │ GraphQL
                            v
                 ┌─────────────────────┐
                 │ Flask Backend       │
                 │ Separate host      │
                 └──────────┬──────────┘
                            │ HTTP
                            v
                 ┌─────────────────────┐
                 │ Node Executor       │
                 │ Separate host       │
                 └──────────┬──────────┘
                            │
                            v
                 ┌─────────────────────┐
                 │ Docker + g++        │
                 └─────────────────────┘
```

Important deployment implication:

> Adding Flask means the application backend is no longer something that can simply live entirely inside a Vercel Next.js deployment.

The Next.js frontend can still be deployed to Vercel, but the Flask API needs a compatible backend host, and the C++ execution service needs infrastructure capable of running Docker.

The exact providers should be selected later based on current free-tier limitations, Docker support, networking, resource limits, and expected usage.

Do not optimize deployment before the local architecture is working.

---

## 19. Team Development Strategy

Because this is a group project, the architecture should make parallel work possible.

A reasonable division is:

### Frontend track

Own:
- Next.js pages;
- Monaco editor;
- exercise UI;
- tags/filtering;
- localStorage;
- result display;
- frontend tests.

### Flask/API track

Own:
- Flask application;
- GraphQL schema;
- exercise queries;
- execution mutation;
- API validation;
- backend tests.

### Executor/infrastructure track

Own:
- Node executor;
- Docker integration;
- compilation;
- timeout/resource handling;
- test harness;
- execution tests;
- security/hardening.

### Shared responsibilities

Everyone should understand:
- the overall architecture;
- how requests flow through the system;
- how to run the project locally;
- the GraphQL schema;
- the execution result format;
- Git workflow and pull requests.

The goal is **division of work without creating silos**. Each team member should be able to explain how their part interacts with the others.

---

## 20. Suggested Git / Collaboration Workflow

Use a shared Git repository with a protected main branch if practical.

A typical workflow:

```text
main
  |
  +-- feature/frontend-exercise-page
  +-- feature/graphql-exercises
  +-- feature/executor-docker
  +-- feature/test-harness
```

Pull requests should ideally include:
- a concise description;
- screenshots for meaningful UI changes;
- tests for important behavior;
- notes about API/schema changes;
- any setup changes required for teammates.

Avoid large unrelated commits that change multiple architectural areas at once.

---

## 21. Documentation

The repository should include enough documentation that a new team member can get started without asking the original author for every step.

At minimum:

### `README.md`

Include:
- project purpose;
- major technologies;
- quick-start instructions;
- repository structure;
- how to run the application.

### `docs/architecture.md`

Explain:
- Next.js;
- Flask;
- GraphQL;
- Node executor;
- Docker;
- C++ test harness;
- request/response flow.

### `docs/development.md`

Explain:
- WSL2 setup;
- Docker setup;
- Python environment;
- Node dependencies;
- running each service;
- common troubleshooting steps.

### `docs/execution-security.md`

Explain:
- why arbitrary C++ is dangerous;
- Docker restrictions;
- timeouts;
- memory/CPU/process limits;
- network isolation;
- what the current sandbox does and does not guarantee.

---

## 22. Milestones

A possible multi-week schedule:

### Milestone 1 — Environment + architecture

- WSL2
- Docker
- Node
- Python
- g++
- Git
- monorepo
- architecture documentation

### Milestone 2 — C++ execution prototype

- Docker compilation
- execution
- timeout
- cleanup

### Milestone 3 — Test harness + executor

- first exercise
- hidden tests
- JSONL
- Node executor

### Milestone 4 — Flask + GraphQL

- exercise queries
- execution mutation
- executor integration
- backend tests

### Milestone 5 — Frontend

- exercise list
- exercise page
- Monaco
- Run
- results

### Milestone 6 — User experience

- localStorage
- solved status
- reset
- tags
- filtering
- additional exercises

### Milestone 7 — Testing + hardening

- integration tests
- security tests
- error handling
- cleanup
- accessibility
- UI polish

### Milestone 8 — Deployment + presentation

- deploy frontend
- deploy Flask backend
- deploy executor
- configure environment variables
- test end-to-end in production
- write documentation
- prepare demo/presentation

The exact number of weeks can be adjusted based on team size and course requirements.

---

## 23. Definition of Done for the First Release

The first release should be considered complete when a new user can:

1. Open the deployed website.
2. Browse a collection of C++ exercises.
3. Filter exercises using tags.
4. Open an exercise.
5. Read its description and examples.
6. Edit starter C++ code.
7. Run the code.
8. Receive useful results from hidden tests.
9. See compilation errors when their code does not compile.
10. See a timeout when execution exceeds the limit.
11. See individual test results when tests fail.
12. See the exercise become solved when all tests pass.
13. Leave and return to the exercise without losing their locally saved code.
14. Reset the code to the starter version.
15. Reset their local progress.

The team should also be able to:

- clone the repository from scratch;
- follow the setup documentation;
- run all services locally;
- add a new exercise;
- understand the GraphQL API;
- understand the execution pipeline;
- run the automated test suite;
- deploy the application.

---

## 24. Learning Goals

This project should be treated as both a software project and a learning project.

### Next.js / React

Learn:
- App Router;
- component architecture;
- client/server boundaries;
- frontend state;
- API integration;
- Monaco integration.

### TypeScript / Node.js

Learn:
- TypeScript project structure;
- HTTP services;
- request validation;
- asynchronous execution;
- process management;
- filesystem operations;
- error handling.

### Flask / Python

Learn:
- Flask application structure;
- routing/resolvers;
- GraphQL schemas;
- validation;
- service-layer design;
- backend testing.

### GraphQL

Learn:
- queries;
- mutations;
- schemas;
- resolvers;
- typed API design;
- frontend/backend contracts.

### Docker

Learn:
- images;
- containers;
- Dockerfiles;
- volumes/mounts;
- resource limits;
- networking;
- container lifecycle;
- isolation concepts.

### C++ execution infrastructure

Learn:
- compilation;
- subprocesses;
- exit codes;
- stdout/stderr;
- test harnesses;
- timeouts;
- untrusted code concerns.

### Software engineering

Learn:
- monorepos;
- Git branches and pull requests;
- API contracts;
- integration testing;
- documentation;
- deployment;
- debugging across services.

---

## 25. What Not to Overbuild

Even though the project is intentionally larger than a tiny MVP, several areas should remain deliberately simple.

### Do not build authentication early

There is no need for accounts before the core exercise experience works.

### Do not add a database just because this is a full-stack project

Exercise content can initially live in the repository, and local progress can live in `localStorage`.

A database becomes useful when persistent user accounts/progress/submissions are actually needed.

### Do not add a queue immediately

A queue/worker architecture may eventually help with scale, but it adds significant infrastructure. First make direct execution reliable.

### Do not support multiple languages immediately

Build the C++ execution pipeline well before generalizing it.

### Do not over-engineer the GraphQL schema

Expose the concepts the current application needs. Add new types and mutations when a real feature requires them.

### Do not treat Docker as the final security architecture

The initial goal is a reasonable isolated execution environment for a project. Public production deployment of arbitrary code requires substantially more security work.

---

## 26. Future Expansion

Once the first release works, the architecture can grow toward:

```text
                     ┌───────────────┐
                     │   Next.js     │
                     │   Frontend    │
                     └───────┬───────┘
                             │
                          GraphQL
                             │
                     ┌───────v───────┐
                     │ Flask Backend  │
                     └───────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              v              v              v
          Database       Executor       Auth/User
              │              │              │
              │              v              │
              │           Docker            │
              │              │              │
              └──────────────┴──────────────┘
```

Potential future features:
- accounts;
- persistent progress;
- submission history;
- saved solutions;
- multiple languages;
- more sophisticated code execution;
- leaderboards;
- personalized exercise recommendations;
- admin tooling;
- analytics;
- larger exercise collections;
- queue-based execution;
- stronger sandboxing.

These are deliberately deferred until the core platform is stable.

---

## 27. Immediate Next Steps

### Step 1 — Finish the development environment

On Windows:

1. Install/verify WSL2.
2. Install Docker Desktop.
3. Enable WSL2 integration for Ubuntu.
4. Verify Docker from Ubuntu.
5. Verify Node/npm.
6. Verify Python.
7. Verify g++.
8. Verify Git.

### Step 2 — Create the monorepo

Create:

```text
coding-platform/
├── web/
├── backend/
├── executor/
├── exercises/
├── docker/
└── docs/
```

### Step 3 — Prove Docker C++ execution

Do not start with the frontend.

First make this work:

```text
C++ source
   -> Docker
   -> g++
   -> executable
   -> output
```

### Step 4 — Build the first exercise

Create `001-sum` with:

- `exercise.md`;
- `starter.cpp`;
- `tests.cpp`.

### Step 5 — Build the executor

Make Node capable of turning:

```text
student code + exercise ID
```

into:

```text
structured execution result
```

### Step 6 — Add Flask + GraphQL

Expose exercises and code execution through the GraphQL API.

### Step 7 — Build the frontend

Connect Next.js to the GraphQL API and build the complete exercise workflow.

### Step 8 — Expand and harden

Add more exercises, tags, persistence, tests, error handling, and security improvements.

### Step 9 — Deploy

Only after the local system is stable should the team decide where the Next.js frontend, Flask backend, and Docker-based executor should be hosted.

---

## 28. Final Architecture Summary

The intended first-release architecture is:

```text
                         USER
                           |
                           v
                ┌─────────────────────┐
                │ Next.js / React     │
                │ TypeScript          │
                │ Monaco Editor       │
                │ localStorage        │
                └──────────┬──────────┘
                           │
                        GraphQL
                           │
                           v
                ┌─────────────────────┐
                │ Flask / Python      │
                │ GraphQL API         │
                │ Application Logic   │
                └──────────┬──────────┘
                           │
                         HTTP
                           │
                           v
                ┌─────────────────────┐
                │ Node.js / TypeScript│
                │ Execution Service   │
                └──────────┬──────────┘
                           │
                           v
                ┌─────────────────────┐
                │ Docker Sandbox      │
                │ Network Disabled    │
                │ Resource Limited    │
                └──────────┬──────────┘
                           │
                           v
                ┌─────────────────────┐
                │ g++ + C++ Harness   │
                │ Hidden Tests        │
                └─────────────────────┘
```

The central design principle remains:

> **Keep the frontend focused on the user experience, keep application/business logic in Flask, and keep untrusted C++ execution isolated in its own Node/Docker execution layer.**

This gives the group enough technical depth for a multi-week project while keeping the responsibilities of each service clear and giving the team a path toward future accounts, persistent data, multiple languages, and stronger execution infrastructure.
