import httpx

from app.db.models import Severity
from app.services.plugins.base import PluginContext, PluginFinding
from app.utils.targets import ensure_url


class RobotsScanner:
    name = "robots_and_security_txt"
    description = "Checks for robots.txt, sitemap.xml, and security.txt hygiene."

    def run(self, context: PluginContext) -> list[PluginFinding]:
        base = ensure_url(context.target).rstrip("/")
        findings: list[PluginFinding] = []

        robots = httpx.get(f"{base}/robots.txt", timeout=context.timeout_seconds)
        security = httpx.get(f"{base}/.well-known/security.txt", timeout=context.timeout_seconds)
        sitemap = httpx.get(f"{base}/sitemap.xml", timeout=context.timeout_seconds)

        if security.status_code != 200:
            findings.append(
                PluginFinding(
                    plugin=self.name,
                    title="security.txt is missing",
                    description="The application does not expose a `security.txt` contact file.",
                    severity=Severity.low,
                    evidence={"url": f"{base}/.well-known/security.txt", "status_code": security.status_code},
                    remediation="Publish a `security.txt` file so researchers have a clear reporting path.",
                    references=["https://securitytxt.org/"],
                )
            )

        if robots.status_code == 200:
            disallow_rules = [line for line in robots.text.splitlines() if line.lower().startswith("disallow:")]
            findings.append(
                PluginFinding(
                    plugin=self.name,
                    title="robots.txt profile recorded",
                    description="Collected robots.txt entries for review and change tracking.",
                    severity=Severity.info,
                    evidence={
                        "url": f"{base}/robots.txt",
                        "disallow_rules": disallow_rules[:20],
                        "rule_count": len(disallow_rules),
                    },
                    remediation="Review disallowed paths to ensure they do not reveal unnecessary environment details.",
                )
            )

        if sitemap.status_code != 200:
            findings.append(
                PluginFinding(
                    plugin=self.name,
                    title="sitemap.xml not found",
                    description="The target does not expose a sitemap document at the default path.",
                    severity=Severity.info,
                    evidence={"url": f"{base}/sitemap.xml", "status_code": sitemap.status_code},
                    remediation="If the application is public-facing, consider publishing a sitemap for indexing hygiene.",
                )
            )

        return findings

