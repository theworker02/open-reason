"""Lightweight PII heuristics. Conservative: flag, then drop in strict mode."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s])?(?:\(?\d{3}\)?[-.\s])?\d{3}[-.\s]\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")

# Common placeholder values that should not be treated as PII.
ALLOWLIST = {
    "user@example.com",
    "test@example.org",
    "admin@example.com",
    "127.0.0.1",
    "0.0.0.0",
    "255.255.255.255",
    "192.0.2.1",
    "198.51.100.1",
    "203.0.113.1",
}


def pii_hits(text: str) -> list[str]:
    hits: list[str] = []
    for match in EMAIL_RE.findall(text):
        if match.lower() not in ALLOWLIST:
            hits.append(f"email:{match}")
    for match in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", match)
        if len(digits) >= 10:
            hits.append("phone")
    if SSN_RE.search(text):
        hits.append("ssn")
    for match in IPV4_RE.findall(text):
        if match not in ALLOWLIST:
            # Documentation IPs in TEST-NET are allowed.
            if not match.startswith(("192.0.2.", "198.51.100.", "203.0.113.", "10.", "172.", "192.168.")):
                hits.append(f"ipv4:{match}")
    return hits
