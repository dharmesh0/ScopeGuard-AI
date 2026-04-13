import dns.resolver

from app.db.models import Severity
from app.services.plugins.base import PluginContext, PluginFinding
from app.utils.targets import extract_hostname


class DNSResolverScanner:
    name = "dns_resolver"
    description = "Collects DNS records for approved targets."

    def run(self, context: PluginContext) -> list[PluginFinding]:
        host = extract_hostname(context.target)
        records = {}
        for record_type in ("A", "AAAA", "MX", "TXT"):
            try:
                answers = dns.resolver.resolve(host, record_type, lifetime=context.timeout_seconds)
                records[record_type] = [answer.to_text() for answer in answers]
            except Exception:
                records[record_type] = []

        return [
            PluginFinding(
                plugin=self.name,
                title="DNS footprint recorded",
                description="Captured baseline DNS data for the approved target.",
                severity=Severity.info,
                evidence={"host": host, "records": records},
                remediation="Review exposed DNS records regularly and retire legacy entries.",
            )
        ]

