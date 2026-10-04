import time, jwt
from .hashing import digest

def mint(secret: str, *, tenant: str, owner: str, agent: str, action: str, target: str,
         max_value: int, tx_hash: str, delegation_root: str, ttl: int):
    now = int(time.time())
    claims = {
        "iss": "agentshield",
        "sub": agent,
        "on_behalf_of": owner,
        "tenant": tenant,
        "action": action,
        "target": target,
        "max_value": str(max_value),
        "tx_hash": tx_hash,
        "delegation_root": delegation_root,
        "iat": now,
        "exp": now + ttl,
        "jti": digest({"agent": agent, "tx": tx_hash, "iat": now}),
    }
    return jwt.encode(claims, secret, algorithm="HS256")
