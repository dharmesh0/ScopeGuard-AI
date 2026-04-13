# Kubernetes Notes

The Docker Compose deployment is intentionally structured so each workload maps cleanly to Kubernetes:

- `api` -> Deployment + Service
- `worker` -> Deployment
- `web` -> Deployment + Service
- `postgres`, `redis`, `neo4j` -> managed services or StatefulSets
- `prometheus`, `grafana` -> monitoring stack or operator-managed resources

Recommended production migration path:

1. Move PostgreSQL, Redis, and Neo4j to managed offerings.
2. Replace Docker socket mounting with a dedicated isolated runner pool or Kubernetes Jobs.
3. Use Sealed Secrets or an external secret manager.
4. Put the API behind an ingress with TLS and WAF policies.
5. Attach NetworkPolicies so runner workloads only reach approved outbound destinations.

