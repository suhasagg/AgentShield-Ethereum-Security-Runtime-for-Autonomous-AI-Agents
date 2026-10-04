from .domain import AgentIdentity

def trust_tier(identity: AgentIdentity) -> tuple[str, int]:
    # Risk-adaptive ceiling; policy may always choose a lower ceiling.
    validation_bonus = 10 if any(v.lower() in {"tee", "zkml", "stake"} for v in identity.validations) else 0
    score = min(100, identity.reputation + validation_bonus)
    if identity.verification_score is not None:
        # ERC-8126 defines lower risk score as safer.
        score = min(score, max(0, 100 - identity.verification_score))
    if score >= 80:
        return "ESTABLISHED", 10_000 * 10**18
    if score >= 50:
        return "TRUSTED", 1_000 * 10**18
    return "NEW", 100 * 10**18
