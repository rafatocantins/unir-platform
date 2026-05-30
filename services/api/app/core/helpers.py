"""Helpers para serialização JSON em campos Text (compatível SQLite e PostgreSQL)."""

import json
from typing import Any, Optional


def json_dumps(value: Optional[Any]) -> Optional[str]:
    """Converte valor para JSON string ou None."""
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def json_loads(value: Optional[str]) -> Optional[Any]:
    """Converte JSON string para Python object ou None."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None
