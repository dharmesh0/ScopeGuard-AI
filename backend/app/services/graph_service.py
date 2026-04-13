from neo4j import GraphDatabase

from app.core.config import get_settings
from app.db.models import Finding, Scan


class GraphService:
    def __init__(self) -> None:
        settings = get_settings()
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    def ensure_constraints(self) -> None:
        queries = [
            "CREATE CONSTRAINT target_id IF NOT EXISTS FOR (t:Target) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT vulnerability_id IF NOT EXISTS FOR (v:Vulnerability) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT remediation_id IF NOT EXISTS FOR (r:Remediation) REQUIRE r.id IS UNIQUE",
        ]
        with self.driver.session() as session:
            for query in queries:
                session.run(query)

    def upsert_scan_graph(self, scan: Scan, findings: list[Finding]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (t:Target {id: $target})
                SET t.last_seen = datetime(), t.scan_id = $scan_id
                """,
                target=scan.target,
                scan_id=str(scan.id),
            )
            for finding in findings:
                session.run(
                    """
                    MERGE (v:Vulnerability {id: $finding_id})
                    SET v.title = $title, v.severity = $severity, v.plugin = $plugin
                    MERGE (t:Target {id: $target})
                    MERGE (t)-[:HAS_FINDING]->(v)
                    MERGE (r:Remediation {id: $remediation_id})
                    SET r.text = $remediation
                    MERGE (v)-[:MITIGATED_BY]->(r)
                    """,
                    finding_id=str(finding.id),
                    title=finding.title,
                    severity=finding.severity.value,
                    plugin=finding.plugin,
                    target=scan.target,
                    remediation_id=f"{finding.id}:remediation",
                    remediation=finding.remediation,
                )

