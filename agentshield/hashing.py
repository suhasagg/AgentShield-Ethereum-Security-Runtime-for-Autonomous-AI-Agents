import hashlib, json
from typing import Any

def canonical(value: Any) -> bytes:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()

def digest(value: Any) -> str:
    return "0x" + hashlib.sha256(canonical(value)).hexdigest()
