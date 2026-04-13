# ScopeGuard AI Architecture

ScopeGuard AI is a defensive, authorization-gated security assessment platform. It keeps the orchestration patterns that teams expect from modern AI-assisted security tooling while explicitly avoiding exploit delivery and unsafe autonomous attack execution.

## Core services

- `api`: FastAPI application exposing REST, GraphQL, JWT auth, WebSocket logs, and Prometheus metrics.
- `worker`: Celery background runner executing assessments and report generation.
- `web`: Next.js dashboard for operators.
- `postgres`: relational state plus `pgvector` memory.
- `neo4j`: relationship graph for targets, findings, and remediation patterns.
- `redis`: Celery broker/result store.
- `prometheus` and `grafana`: monitoring.

## Execution model

1. A user creates an engagement with a clearly defined scope.
2. A scan request is validated against the approved scope and permission attestation.
3. The coordinator agent runs built-in safe plugins inside resource-limited Docker containers.
4. Findings are normalized, enriched with memory and CVE context, and persisted.
5. Reporting artifacts are produced in Markdown and PDF.

## Safety controls

- Explicit authorization attestations and scope validation.
- Optional human approval checkpoints.
- No exploit execution or weaponized payload delivery.
- Resource-limited container runner with dropped Linux capabilities and read-only filesystem.
