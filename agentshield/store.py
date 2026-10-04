from .models import DecisionRecord
from .db import Session
from .domain import AnalyzeRequest, AnalysisVerdict

async def persist(req: AnalyzeRequest, verdict: AnalysisVerdict):
    async with Session() as s:
        s.add(DecisionRecord(
            tenant_id=req.identity.tenant_id,
            agent_id=req.identity.agent_id,
            tx_hash=verdict.transaction_hash,
            intent_hash=verdict.intent_hash,
            delegation_root=verdict.delegation_root,
            provenance_root=verdict.provenance_root,
            decision=verdict.decision.value,
            risk_score=verdict.risk_score,
            reasons=verdict.reasons,
            policy_version=verdict.policy_version,
        ))
        await s.commit()
