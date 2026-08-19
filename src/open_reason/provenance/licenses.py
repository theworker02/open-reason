"""License policy for ingestion and validation."""

from __future__ import annotations

from dataclasses import dataclass

# SPDX identifiers considered compatible with Open Reason redistribution
# for *original or permissively licensed* material. Copyleft source may be
# ingested only when the example is a short, clearly attributed excerpt and
# the downstream dataset license remains a conjunction of licenses — the
# pipeline records the original SPDX and does not relicense it.
PERMISSIVE_SPDX = frozenset(
    {
        "Apache-2.0",
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "ISC",
        "CC0-1.0",
        "CC-BY-4.0",
        "CC-BY-3.0",
        "Unlicense",
        "0BSD",
        "Python-2.0",
        "Zlib",
        "MPL-2.0",
        "ODbL-1.0",
        "ODC-By-1.0",
        "PDDL-1.0",
    }
)

SHARE_ALIKE_SPDX = frozenset(
    {
        "CC-BY-SA-4.0",
        "CC-BY-SA-3.0",
        "CC-BY-SA-2.5",
    }
)

COPYLEFT_SPDX = frozenset(
    {
        "GPL-2.0",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "AGPL-3.0",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "LGPL-2.1",
        "LGPL-3.0",
    }
)

REJECTED_SPDX = frozenset(
    {
        "NOASSERTION",
        "NONE",
        "UNKNOWN",
        "UNLICENSED",
        "PROPRIETARY",
        "ALL-RIGHTS-RESERVED",
    }
)


@dataclass(frozen=True)
class LicenseDecision:
    allowed: bool
    reason: str
    spdx: str | None


def normalize_spdx(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def evaluate_license(spdx: str | None, *, allow_copyleft: bool = False) -> LicenseDecision:
    identifier = normalize_spdx(spdx)
    if identifier is None:
        return LicenseDecision(False, "license is missing", None)
    upper = identifier.upper()
    if identifier in REJECTED_SPDX or upper in REJECTED_SPDX:
        return LicenseDecision(False, f"license {identifier} is not redistributable", identifier)
    if identifier in PERMISSIVE_SPDX:
        return LicenseDecision(True, "permissive license", identifier)
    if identifier in SHARE_ALIKE_SPDX:
        return LicenseDecision(
            True,
            "share-alike kept on the row; not relicensed as the project license",
            identifier,
        )
    if identifier in COPYLEFT_SPDX:
        if allow_copyleft:
            return LicenseDecision(True, "copyleft allowed by source policy", identifier)
        return LicenseDecision(
            False,
            f"copyleft license {identifier} requires an explicit source policy exception",
            identifier,
        )
    return LicenseDecision(
        False,
        f"license {identifier} is not in the allowlist; add it explicitly after legal review",
        identifier,
    )
