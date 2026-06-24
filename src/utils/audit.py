from __future__ import annotations

import json
from datetime import UTC, datetime

from src.utils.config import BASE_DIR


def audit_log(actor: str, action: str, metadata: dict | None = None) -> None:
    path = BASE_DIR / "reports" / "audit.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor": actor,
        "action": action,
        "metadata": metadata or {},
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
