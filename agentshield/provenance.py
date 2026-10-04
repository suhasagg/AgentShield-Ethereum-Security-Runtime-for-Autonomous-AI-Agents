from .domain import ProvenanceSignal, TrustLevel
from .hashing import digest

def evaluate(signals: list[ProvenanceSignal]):
    normalized = []
    untrusted = False
    for s in signals:
        item = s.model_copy()
        if not item.content_hash:
            item.content_hash = digest({"source": item.source, "labels": item.labels})
        normalized.append(item)
        untrusted |= item.trust == TrustLevel.UNTRUSTED
    root = digest([x.model_dump(mode="json") for x in normalized])
    return normalized, root, untrusted
