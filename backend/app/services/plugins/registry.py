from app.services.plugins.base import ScannerPlugin
from app.services.scanners.dns_resolver import DNSResolverScanner
from app.services.scanners.http_headers import HTTPHeadersScanner
from app.services.scanners.robots import RobotsScanner
from app.services.scanners.tls_inspector import TLSInspectorScanner


def builtin_plugins() -> dict[str, ScannerPlugin]:
    return {
        scanner.name: scanner
        for scanner in [
            DNSResolverScanner(),
            HTTPHeadersScanner(),
            TLSInspectorScanner(),
            RobotsScanner(),
        ]
    }


def list_plugins() -> list[dict]:
    return [
        {"name": plugin.name, "description": plugin.description, "source": "builtin"}
        for plugin in builtin_plugins().values()
    ]


def load_plugin(name: str) -> ScannerPlugin:
    plugins = builtin_plugins()
    if name not in plugins:
        raise KeyError(f"Unknown plugin: {name}")
    return plugins[name]
