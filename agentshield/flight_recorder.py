from .hashing import digest

def event(session: str, seq: int, kind: str, payload: dict, parents: list[str] | None = None):
    body = {"session": session, "seq": seq, "kind": kind, "payload": payload, "parents": parents or []}
    return {**body, "event_hash": digest(body)}
