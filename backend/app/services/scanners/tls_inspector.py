import socket
import ssl
from datetime import UTC, datetime

from app.db.models import Severity
from app.services.plugins.base import PluginContext, PluginFinding
from app.utils.targets import extract_hostname


class TLSInspectorScanner:
    name = "tls_inspector"
    description = "Collects certificate and protocol metadata from the target's TLS endpoint."

    def run(self, context: PluginContext) -> list[PluginFinding]:
        host = extract_hostname(context.target)
        findings: list[PluginFinding] = []
        ssl_context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=context.timeout_seconds) as sock:
            with ssl_context.wrap_socket(sock, server_hostname=host) as tls_socket:
                cert = tls_socket.getpeercert()
                protocol = tls_socket.version()

        expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
        days_remaining = (expiry - datetime.now(UTC)).days

        if protocol in {"TLSv1", "TLSv1.1"}:
            findings.append(
                PluginFinding(
                    plugin=self.name,
                    title="Legacy TLS protocol negotiated",
                    description=f"The endpoint negotiated {protocol}, which should be retired.",
                    severity=Severity.medium,
                    evidence={"protocol": protocol, "host": host},
                    remediation="Disable TLSv1.0 and TLSv1.1 on the server and any intermediary proxies.",
                )
            )

        if days_remaining < 0:
            severity = Severity.high
            title = "TLS certificate has expired"
        elif days_remaining < 21:
            severity = Severity.medium
            title = "TLS certificate nearing expiration"
        else:
            severity = Severity.info
            title = "TLS certificate status recorded"

        findings.append(
            PluginFinding(
                plugin=self.name,
                title=title,
                description="Captured certificate metadata for the approved endpoint.",
                severity=severity,
                evidence={
                    "host": host,
                    "days_remaining": days_remaining,
                    "subject": dict(item[0] for item in cert.get("subject", [])),
                    "issuer": dict(item[0] for item in cert.get("issuer", [])),
                    "protocol": protocol,
                },
                remediation="Track certificate validity in operations monitoring and renew ahead of time.",
            )
        )
        return findings

