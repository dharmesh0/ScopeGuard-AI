from urllib.parse import urlparse


def ensure_url(target: str) -> str:
    parsed = urlparse(target)
    if parsed.scheme:
        return target
    return f"https://{target}"


def extract_hostname(target: str) -> str:
    parsed = urlparse(ensure_url(target))
    return parsed.hostname or target


def match_scope(target: str, scope: list[str]) -> bool:
    normalized_target = ensure_url(target)
    target_host = extract_hostname(normalized_target)
    for rule in scope:
        normalized_rule = rule.strip()
        if not normalized_rule:
            continue
        if normalized_rule.startswith("http://") or normalized_rule.startswith("https://"):
            if normalized_target.startswith(normalized_rule):
                return True
            continue
        if normalized_rule.startswith("*."):
            suffix = normalized_rule[2:]
            if target_host == suffix or target_host.endswith(f".{suffix}"):
                return True
            continue
        if target_host == normalized_rule or target_host.endswith(f".{normalized_rule}"):
            return True
    return False

