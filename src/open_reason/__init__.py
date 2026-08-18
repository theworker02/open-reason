"""Open Reason: an open, verified dataset for coding, science, mathematics, and reasoning."""

from __future__ import annotations

__version__ = "1.0.0"
__pipeline_version__ = "1.0.0"

from open_reason.models import Example, Provenance, Quality, Verification

__all__ = [
    "Example",
    "Provenance",
    "Quality",
    "Verification",
    "__pipeline_version__",
    "__version__",
]
