from time import time
from .domain import AgentIdentity, DelegationHop
from .hashing import digest

def verify_chain(identity: AgentIdentity, hops: list[DelegationHop], now: int | None = None):
    now = now or int(time())
    if not hops:
        return [], 2**256 - 1, digest({"owner": identity.owner_address, "agent": identity.agent_address}), []
    reasons = []
    expected = identity.owner_address.lower()
    effective = None
    max_value = 2**256 - 1
    previous_digest = None
    for depth, hop in enumerate(hops, start=1):
        if hop.delegator.lower() != expected:
            reasons.append(f"BROKEN_DELEGATION_CHAIN_AT_{depth}")
        if hop.valid_until < now:
            reasons.append(f"EXPIRED_DELEGATION_AT_{depth}")
        if previous_digest and hop.parent_digest != previous_digest:
            reasons.append(f"PARENT_DIGEST_MISMATCH_AT_{depth}")
        caps = set(hop.capabilities)
        effective = caps if effective is None else effective.intersection(caps)
        max_value = min(max_value, hop.max_value_wei)
        previous_digest = digest(hop.model_dump(exclude={"signature"}))
        expected = hop.delegatee.lower()
    if expected != identity.agent_address.lower():
        reasons.append("DELEGATION_NOT_BOUND_TO_EXECUTING_AGENT")
    return sorted(effective or []), max_value, digest([h.model_dump() for h in hops]), reasons
