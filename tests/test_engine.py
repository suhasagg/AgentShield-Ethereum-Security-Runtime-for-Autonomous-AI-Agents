import pytest, time
from agentshield.domain import *
from agentshield.engine import AgentShieldEngine

OWNER="0x0000000000000000000000000000000000000001"
AGENT="0x0000000000000000000000000000000000000002"
ROUTER="0x0000000000000000000000000000000000000003"

def request(**kw):
    now=int(time.time())
    base=AnalyzeRequest(
        identity=AgentIdentity(
            tenant_id="acme", agent_id="portfolio-1", agent_address=AGENT,
            owner_address=OWNER, erc8004_agent_id=7, reputation=90,
            verification_score=10, validations=["TEE"]
        ),
        delegation=[DelegationHop(
            delegator=OWNER, delegatee=AGENT, capabilities=["eth:swap"],
            max_value_wei=5*10**18, valid_until=now+3600, nonce=1
        )],
        provenance=[ProvenanceSignal(source="user", trust="TRUSTED")],
        intent=TransactionIntent(
            goal="Convert 5 ETH to USDC", action="swap", token_in="ETH", token_out="USDC",
            amount_in=5*10**18, max_slippage_bps=50, recipient=OWNER,
            approved_routers=[ROUTER], max_new_approval=5*10**18
        ),
        transaction=ProposedTransaction(
            chain_id=1, sender=AGENT, target=ROUTER, value=5*10**18, calldata="0x1234"
        ),
        simulation=SimulationResult(
            success=True, decoded_action="swapExactInput",
            asset_flows=[AssetFlow(asset="USDC", sender=ROUTER, recipient=OWNER, amount=10000_000000, direction="in")],
            state_diff=StateDiff(), mev_risk=5, contract_risk=5
        )
    )
    return base.model_copy(update=kw)

@pytest.mark.asyncio
async def test_safe_swap_allowed():
    v=await AgentShieldEngine().analyze(request())
    assert v.decision == Decision.ALLOW
    assert v.capability_token

@pytest.mark.asyncio
async def test_unlimited_approval_blocked():
    r=request()
    r.simulation.state_diff.approvals=[{"token":"USDC","spender":ROUTER,"amount":2**256-1}]
    v=await AgentShieldEngine().analyze(r)
    assert v.decision == Decision.BLOCK
    assert "TOKEN_APPROVAL_EXCEEDS_INTENT" in v.reasons

@pytest.mark.asyncio
async def test_untrusted_input_requires_review():
    r=request(provenance=[ProvenanceSignal(source="web", trust="UNTRUSTED", labels=["indirect-prompt-injection"])])
    v=await AgentShieldEngine().analyze(r)
    assert v.decision in {Decision.REVIEW, Decision.BLOCK}

@pytest.mark.asyncio
async def test_privilege_laundering_denied():
    r=request()
    r.delegation[0].capabilities=["eth:read"]
    v=await AgentShieldEngine().analyze(r)
    assert v.decision == Decision.BLOCK
