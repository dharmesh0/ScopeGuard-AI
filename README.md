# ScopeGuard AI

ScopeGuard AI is a production-style, open-source platform for **authorized** AI-assisted security assessments. It keeps the architectural strengths of a modern automated testing stack, including sandboxed execution, background workers, semantic memory, a knowledge graph, monitoring, and a polished operator UI, while explicitly avoiding exploit delivery and unsafe offensive automation.


## Ethical and legal use

This project is for **legal, authorized security testing only**.

- Do not use it against systems, applications, or infrastructure you do not own or have written permission to assess.
- The platform includes authorization attestations, scope checks, approval workflows, and human-in-the-loop controls to reinforce lawful operation.
- The open-source build intentionally focuses on scanning, defensive analysis, enrichment, and reporting.
- It does **not** ship exploit payloads, weaponized chains, or autonomous intrusion logic.

## 1. Project Overview

### What it does

- Runs safe assessment plugins in isolated Docker containers with resource limits.
- Uses a multi-agent workflow for reconnaissance, analysis, and reporting.
- Stores past run context in PostgreSQL with `pgvector` embeddings.
- Maps targets, findings, and remediations into Neo4j.
- Exposes REST, GraphQL, and WebSocket interfaces.
- Ships a Next.js dashboard for operators and reviewers.
- Includes Prometheus metrics and Grafana dashboard provisioning.

### Core stack

- Backend: FastAPI, SQLAlchemy, Celery, Redis
- Data: PostgreSQL + `pgvector`, Neo4j
- Frontend: Next.js App Router, React, Tailwind CSS
- Infra: Docker Compose, Prometheus, Grafana
- AI: provider abstraction for OpenAI, Anthropic, Ollama, plus a deterministic fallback provider

## 2. Folder Structure

```text
.
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- README.md
|-- LICENSE
|-- backend
|   |-- pyproject.toml
|   `-- app
|       |-- cli.py
|       |-- main.py
|       |-- metrics.py
|       |-- sandbox_runner.py
|       |-- api
|       |-- core
|       |-- db
|       |-- schemas
|       |-- services
|       |-- tasks
|       |-- templates
|       `-- utils
|-- docs
|   |-- ARCHITECTURE.md
|   |-- ROADMAP.md
|   `-- SETUP.md
|-- frontend
|   |-- app
|   |-- components
|   |-- lib
|   |-- package.json
|   |-- tailwind.config.ts
|   `-- tsconfig.json
|-- infra
|   |-- docker
|   |-- grafana
|   |-- k8s
|   `-- prometheus
`-- storage
    `-- reports
```

## 3. Step-by-Step Backend Implementation

1. FastAPI app bootstraps in [`backend/app/main.py`](backend/app/main.py), creates tables, provisions a default admin, enables metrics, and sets up CORS, GraphQL, and WebSocket log streaming.
2. Security and configuration live in [`backend/app/core`](backend/app/core), including JWT creation, password hashing, settings loading, and rate limiting.
3. Relational models are defined in [`backend/app/db/models.py`](backend/app/db/models.py), covering users, engagements, approvals, scans, findings, memory entries, and reports.
4. REST routes in [`backend/app/api/rest`](backend/app/api/rest) handle authentication, engagements, approvals, scans, reports, plugins, intelligence, and health.
5. Celery workers in [`backend/app/tasks`](backend/app/tasks) process queued scan jobs asynchronously through Redis.
6. The container runner in [`backend/app/services/container/manager.py`](backend/app/services/container/manager.py) spawns isolated tool containers with dropped capabilities, read-only filesystems, and CPU/memory limits.
7. Safe assessment plugins in [`backend/app/services/scanners`](backend/app/services/scanners) collect HTTP, TLS, DNS, and disclosure hygiene data without exploit execution.
8. Semantic memory in [`backend/app/services/memory_service.py`](backend/app/services/memory_service.py) stores scan summaries and retrieves similar prior context using `pgvector`.
9. Knowledge graph sync in [`backend/app/services/graph_service.py`](backend/app/services/graph_service.py) maps targets, vulnerabilities, and remediation links into Neo4j.
10. Markdown and PDF reporting are generated in [`backend/app/services/report_service.py`](backend/app/services/report_service.py).

## 4. Step-by-Step Frontend Implementation

1. Next.js App Router entrypoints live under [`frontend/app`](frontend/app).
2. [`frontend/app/login/page.tsx`](frontend/app/login/page.tsx) provides login and lightweight registration behavior.
3. [`frontend/app/page.tsx`](frontend/app/page.tsx) renders the operator dashboard with scan stats, recent assessments, plugins, and CVE context.
4. [`frontend/app/scans/new/page.tsx`](frontend/app/scans/new/page.tsx) combines engagement creation and scan request creation into one guided workflow.
5. [`frontend/app/scans/[id]/page.tsx`](frontend/app/scans/[id]/page.tsx) shows live scan state, findings, and WebSocket logs.
6. [`frontend/app/reports/[id]/page.tsx`](frontend/app/reports/[id]/page.tsx) displays Markdown reports and links to generated PDFs.
7. Shared API utilities, token storage, and types live under [`frontend/lib`](frontend/lib).
8. Reusable UI building blocks live in [`frontend/components`](frontend/components).

## 5. AI Agent Logic

The agent system is intentionally structured as a **coordinator plus role-specific workers**:

- `ReconAgent`: runs the built-in safe plugins inside isolated runner containers.
- `AnalysisAgent`: combines findings, semantic memory, and latest CVE summaries, then asks the configured LLM provider for a defensive summary.
- `ReportingAgent`: finalizes the operator-facing output package.
- `CoordinatorAgent`: orchestrates the sequence and persists results, memory entries, graph relationships, and reports.

### Execution flow

1. Validate that the requested target matches engagement scope.
2. Require operator attestation and optional admin approval.
3. Queue the scan through Celery.
4. Run safe plugins in sandboxed containers.
5. Retrieve relevant memory from prior scans.
6. Pull safe CVE summaries for enrichment.
7. Generate a prioritized defensive summary.
8. Persist findings, graph data, and report artifacts.

## 6. Database Schema

### PostgreSQL / pgvector

Defined in:

- [`backend/app/db/models.py`](backend/app/db/models.py)
- [`backend/app/db/schema.sql`](backend/app/db/schema.sql)

Main tables:

- `users`
- `engagements`
- `approvals`
- `scans`
- `scan_logs`
- `findings`
- `memory_entries`
- `reports`

`memory_entries.embedding` uses `vector(64)` for lightweight semantic retrieval in the open-source build.

### Neo4j graph model

Defined in:

- [`backend/app/db/graph.cypher`](backend/app/db/graph.cypher)

Main entities:

- `(:Target)`
- `(:Vulnerability)`
- `(:Remediation)`

Relationships:

- `(:Target)-[:HAS_FINDING]->(:Vulnerability)`
- `(:Vulnerability)-[:MITIGATED_BY]->(:Remediation)`

## 7. API Routes

### REST

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Authenticate and issue JWT |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `GET` | `/api/v1/engagements` | List engagements |
| `POST` | `/api/v1/engagements` | Create engagement |
| `GET` | `/api/v1/approvals` | List approval requests |
| `POST` | `/api/v1/approvals` | Create approval request |
| `POST` | `/api/v1/approvals/{approval_id}/decision` | Approve or reject |
| `GET` | `/api/v1/scans/dashboard` | Dashboard metrics |
| `GET` | `/api/v1/scans` | List scans |
| `POST` | `/api/v1/scans` | Create scan |
| `GET` | `/api/v1/scans/{scan_id}` | Scan detail |
| `GET` | `/api/v1/scans/{scan_id}/logs` | Scan logs |
| `POST` | `/api/v1/scans/{scan_id}/resume` | Resume approved scan |
| `GET` | `/api/v1/reports/scan/{scan_id}` | Report metadata |
| `GET` | `/api/v1/reports/scan/{scan_id}/markdown` | Markdown report |
| `GET` | `/api/v1/reports/scan/{scan_id}/pdf` | PDF report |
| `GET` | `/api/v1/plugins` | List built-in plugins |
| `GET` | `/api/v1/intelligence/latest-cves` | Safe latest CVE summaries |

### GraphQL

- `POST /graphql`
- Query fields:
  - `dashboard`
  - `scans`
  - `plugins`

### WebSocket

- `GET /ws/scans/{scan_id}?token=<jwt>`
- Streams new log entries as the worker writes them.

## 8. Docker Setup

Compose services are declared in [`docker-compose.yml`](docker-compose.yml):

- `postgres`
- `redis`
- `neo4j`
- `api`
- `worker`
- `web`
- `prometheus`
- `grafana`

Container runner safeguards:

- read-only filesystem
- dropped Linux capabilities
- `no-new-privileges`
- CPU and memory caps
- timeout-controlled execution

Production note: the local Compose deployment mounts the Docker socket for simplicity. In production, replace that with a dedicated isolated runner pool or Kubernetes Jobs.

## 9. Environment Variables

Use [`./.env.example`](.env.example) as the baseline.

Important variables:

- `SECRET_KEY`
- `DATABASE_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_BASE_URL`
- `SANDBOX_RUNNER_IMAGE`
- `SANDBOX_CPU_LIMIT`
- `SANDBOX_MEMORY_LIMIT`
- `REPORTS_DIR`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`

## 10. README.md

This file is intended to be the GitHub landing page for the project. It includes:

- overview
- ethical constraints
- architecture
- setup
- API inventory
- data model
- deployment notes
- roadmap

## 11. Setup Guide

See the full guide in [`docs/SETUP.md`](docs/SETUP.md).

Quick local start:

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web UI: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
- GraphQL: [http://localhost:8000/graphql](http://localhost:8000/graphql)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3001](http://localhost:3001)

Default admin credentials come from `.env`.

## 12. Future Roadmap

See the detailed roadmap in [`docs/ROADMAP.md`](docs/ROADMAP.md).

Highlights:

- external plugin packages with signed manifests
- richer approval policy engine and audit trails
- managed runner pools instead of Docker socket mounting
- stronger graph analytics and exposure scoring
- Kubernetes-native job orchestration
- SSO, SCIM, and enterprise secrets integration

## Current safe plugin set

The OSS MVP ships with safe built-in plugins:

- DNS footprint collection
- TLS inspection
- HTTP security header review
- `robots.txt`, `sitemap.xml`, and `security.txt` hygiene checks

## What this repository intentionally does not include

- weaponized exploit payloads
- autonomous exploitation loops
- unsafe wrappers around offensive tooling
- target bypass logic or scope evasion

## License

MIT. See [`LICENSE`](LICENSE).
