from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Decision(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "HUMAN_REVIEW"
    BLOCK = "BLOCK"

class TrustLevel(str, Enum):
    TRUSTED = "TRUSTED"
    UNTRUSTED = "UNTRUSTED"
    UNKNOWN = "UNKNOWN"

class AgentIdentity(BaseModel):
    tenant_id: str
    agent_id: str
    agent_address: str
    owner_address: str
    erc8004_agent_id: int | None = None
    reputation: int = Field(default=0, ge=0, le=100)
    verification_score: int | None = Field(default=None, ge=0, le=100)
    validations: list[str] = []

class DelegationHop(BaseModel):
    delegator: str
    delegatee: str
    capabilities: list[str]
    max_value_wei: int = Field(ge=0)
    valid_until: int
    nonce: int
    parent_digest: str | None = None
    signature: str | None = None

class ProvenanceSignal(BaseModel):
    source: str
    trust: TrustLevel = TrustLevel.UNKNOWN
    content_hash: str | None = None
    parent_hashes: list[str] = []
    labels: list[str] = []

class TransactionIntent(BaseModel):
    goal: str
    action: str
    token_in: str | None = None
    token_out: str | None = None
    amount_in: int | None = None
    max_slippage_bps: int | None = None
    recipient: str | None = None
    approved_routers: list[str] = []
    forbid_delegatecall: bool = True
    max_new_approval: int | None = None
    max_mev_risk: int = 40
    max_contract_risk: int = 40

class ProposedTransaction(BaseModel):
    chain_id: int
    sender: str
    target: str
    value: int = Field(ge=0)
    calldata: str
    nonce: int | None = None

class AssetFlow(BaseModel):
    asset: str
    sender: str
    recipient: str
    amount: int
    direction: str

class StateDiff(BaseModel):
    approvals: list[dict[str, Any]] = []
    storage_changes: list[dict[str, Any]] = []
    balance_changes: list[dict[str, Any]] = []

class SimulationResult(BaseModel):
    success: bool
    decoded_action: str | None = None
    decoded_args: dict[str, Any] = {}
    asset_flows: list[AssetFlow] = []
    state_diff: StateDiff = StateDiff()
    uses_delegatecall: bool = False
    revert_reason: str | None = None
    gas_used: int | None = None
    mev_risk: int = 0
    contract_risk: int = 0

class AnalyzeRequest(BaseModel):
    identity: AgentIdentity
    delegation: list[DelegationHop] = []
    provenance: list[ProvenanceSignal] = []
    intent: TransactionIntent
    transaction: ProposedTransaction
    simulation: SimulationResult | None = None

class AnalysisVerdict(BaseModel):
    decision: Decision
    risk_score: int
    reasons: list[str]
    intent_hash: str
    transaction_hash: str
    delegation_root: str
    provenance_root: str
    policy_version: str
    capability_token: str | None = None
    erc8196_action: dict[str, Any] | None = None
