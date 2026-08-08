from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId


def object_id(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def serialize(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key == "_id":
                out["id"] = serialize(item)
            else:
                out[key] = serialize(item)
        return out
    if isinstance(value, list):
        return [serialize(v) for v in value]
    if isinstance(value, tuple):
        return [serialize(v) for v in value]
    return value
