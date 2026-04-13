from urllib.parse import urlparse

import httpx

from app.db.models import Severity
from app.services.plugins.base import PluginContext, PluginFinding
from app.utils.targets import ensure_url


class HTTPHeadersScanner:
    name = "http_headers"
    description = "Inspects security-related HTTP headers and technology exposure."

    def run(self, context: PluginContext) -> list[PluginFinding]:
        findings: list[PluginFinding] = []
        url = ensure_url(context.target)
        response = httpx.get(url, follow_redirects=True, timeout=context.timeout_seconds)
        headers = {key.lower(): value for key, value in response.headers.items()}
        required_headers = {
            "strict-transport-security": ("Missing HSTS header", Severity.medium),
            "content-security-policy": ("Missing Content-Security-Policy header", Severity.medium),
            "x-content-type-options": ("Missing X-Content-Type-Options header", Severity.low),
            "referrer-policy": ("Missing Referrer-Policy header", Severity.low),
        }

        for header, (title, severity) in required_headers.items():
            if header not in headers:
                findings.append(
                    PluginFinding(
                        plugin=self.name,
                        title=title,
                        description=f"The response from {response.url} did not include `{header}`.",
                        severity=severity,
                        evidence={"url": str(response.url), "status_code": response.status_code, "headers": headers},
                        remediation=f"Add and validate the `{header}` security header at the edge or application layer.",
                    )
                )

        exposed = {key: headers[key] for key in ("server", "x-powered-by") if key in headers}
        if exposed:
            findings.append(
                PluginFinding(
                    plugin=self.name,
                    title="Technology disclosure in response headers",
                    description="The application exposes implementation details in HTTP headers.",
                    severity=Severity.info,
                    evidence={"url": str(response.url), "exposed_headers": exposed},
                    remediation="Minimize identifying server framework headers where possible.",
                )
            )

        findings.append(
            PluginFinding(
                plugin=self.name,
                title="HTTP surface summary",
                description="Collected a baseline HTTP response profile for the approved target.",
                severity=Severity.info,
                evidence={
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "content_type": headers.get("content-type", "unknown"),
                    "hostname": urlparse(str(response.url)).hostname,
                },
                remediation="Use this profile as a baseline and compare across environments.",
            )
        )
        return findings

