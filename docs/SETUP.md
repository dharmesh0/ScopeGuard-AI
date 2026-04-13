# Setup Guide

## Local development

1. Copy `.env.example` to `.env`.
2. Review and rotate `SECRET_KEY`, `DEFAULT_ADMIN_PASSWORD`, and database credentials.
3. Start the stack:

```bash
docker compose up --build
```

4. Log into the UI at `http://localhost:3000`.
5. Create an engagement or use the default admin account to approve queued scans.

## Local URLs

- API docs: `http://localhost:8000/docs`
- GraphQL: `http://localhost:8000/graphql`
- Web UI: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Neo4j browser: `http://localhost:7474`

## Production checklist

1. Replace the Docker socket mount with isolated runner infrastructure.
2. Put PostgreSQL, Redis, and Neo4j behind managed services where possible.
3. Rotate all secrets and store them in a secret manager.
4. Run the API behind TLS and an ingress or reverse proxy with WAF controls.
5. Enforce outbound egress rules for runner workloads.
6. Replace default admin provisioning with your identity provider or bootstrap runbook.
7. Route logs to a centralized SIEM or observability pipeline.
8. Back up the `storage/reports` volume and databases.

## Notes

- The open-source build uses safe defensive plugins only.
- The fallback LLM provider works without external API keys for deterministic local demos.
- PDF reports are written to `storage/reports`.

