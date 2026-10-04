from .config import settings
from .domain import AnalyzeRequest, AnalysisVerdict, Decision
from .hashing import digest
from .delegation import verify_chain
from .provenance import evaluate
from .identity import trust_tier
from .intent import compare
from .risk import score
from .capability import mint

class AgentShieldEngine:
    async def analyze(self, req: AnalyzeRequest) -> AnalysisVerdict:
        sim = req.simulation
        if sim is None:
            # Fail closed: execution-grade authorization requires simulation evidence.
            from .domain import SimulationResult
            sim = SimulationResult(success=False, revert_reason="simulation evidence missing")

        caps, delegated_max, delegation_root, delegation_reasons = verify_chain(req.identity, req.delegation)
        _, provenance_root, untrusted = evaluate(req.provenance)
        intent_reasons = compare(req.intent, req.transaction, sim)

        tier, trust_ceiling = trust_tier(req.identity)
        reasons = [*delegation_reasons, *intent_reasons]
        needed_cap = f"eth:{req.intent.action.lower()}"

        if req.delegation and needed_cap not in caps and "eth:*" not in caps:
            reasons.append("DELEGATION_MISSING_REQUIRED_CAPABILITY")
        if req.transaction.value > delegated_max:
            reasons.append("TRANSACTION_EXCEEDS_DELEGATED_VALUE")
        if req.transaction.value > trust_ceiling:
            reasons.append(f"TRANSACTION_EXCEEDS_{tier}_TRUST_CEILING")

        tx_hash = digest(req.transaction)
        intent_hash = digest(req.intent)
        risk = score(
            intent_reasons=reasons,
            delegation_reasons=delegation_reasons,
            untrusted=untrusted,
            side_effect=True,
            reputation=req.identity.reputation,
            sim_mev=sim.mev_risk,
            sim_contract=sim.contract_risk,
        )

        hard_block = bool(delegation_reasons) or any(x in reasons for x in {
            "DELEGATION_MISSING_REQUIRED_CAPABILITY",
            "TRANSACTION_EXCEEDS_DELEGATED_VALUE",
            "DELEGATECALL_FORBIDDEN",
            "TOKEN_APPROVAL_EXCEEDS_INTENT",
            "SIMULATION_REVERTED",
        })
        if hard_block or risk >= settings.block_threshold:
            decision = Decision.BLOCK
        elif untrusted or reasons or risk >= settings.human_review_threshold:
            decision = Decision.REVIEW
        else:
            decision = Decision.ALLOW

        token = None
        erc_action = None
        if decision == Decision.ALLOW:
            token = mint(
                settings.api_key,
                tenant=req.identity.tenant_id,
                owner=req.identity.owner_address,
                agent=req.identity.agent_address,
                action=req.intent.action,
                target=req.transaction.target,
                max_value=min(delegated_max, trust_ceiling),
                tx_hash=tx_hash,
                delegation_root=delegation_root,
                ttl=settings.capability_ttl_seconds,
            )
            erc_action = {
                "agent": req.identity.agent_address,
                "action": req.intent.action,
                "target": req.transaction.target,
                "value": str(req.transaction.value),
                "data": req.transaction.calldata,
                "policyHash": digest({
                    "intent": intent_hash,
                    "delegation": delegation_root,
                    "provenance": provenance_root,
                    "version": settings.policy_version,
                }),
            }

        return AnalysisVerdict(
            decision=decision,
            risk_score=risk,
            reasons=reasons,
            intent_hash=intent_hash,
            transaction_hash=tx_hash,
            delegation_root=delegation_root,
            provenance_root=provenance_root,
            policy_version=settings.policy_version,
            capability_token=token,
            erc8196_action=erc_action,
        )
