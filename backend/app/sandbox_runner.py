import argparse
import json

from app.db.models import Severity
from app.services.plugins.base import PluginContext
from app.services.plugins.registry import load_plugin


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    plugin = load_plugin(args.plugin)
    findings = plugin.run(PluginContext(target=args.target))
    payload = []
    for item in findings:
        payload.append(
            {
                "plugin": item.plugin,
                "title": item.title,
                "description": item.description,
                "severity": item.severity.value if isinstance(item.severity, Severity) else str(item.severity),
                "evidence": item.evidence,
                "remediation": item.remediation,
                "references": item.references,
            }
        )
    print(json.dumps(payload))


if __name__ == "__main__":
    main()

