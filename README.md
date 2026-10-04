# AgentShield — Ethereum Security Runtime for Autonomous AI Agents

> **Firewall + IAM + EDR + transaction simulator for Ethereum AI agents.**

AgentShield is an independent, production-oriented reference architecture and runnable implementation for securing autonomous agents that can propose Ethereum transactions. It deliberately places a deterministic security boundary between probabilistic model reasoning and irreversible financial execution.

It uses public Ethereum standards as interoperability targets and adds an original runtime architecture around identity, trust, delegation, provenance, simulation, intent verification, risk, execution gating, and flight recording.

---

## 1. Executive summary

An AI agent should never receive a private key and be trusted to "do the right thing." The model may be prompt-injected, its retrieved context may be poisoned, its tool output may be wrong, a router may be malicious, calldata may not match the natural-language goal, or a sub-agent may attempt to manufacture authority.

AgentShield converts:

```text
human goal
   +
agent identity
   +
delegated authority
   +
retrieval/tool provenance
   +
proposed Ethereum transaction
   +
forked-EVM simulation evidence
```

into a deterministic decision:

```text
ALLOW
HUMAN_REVIEW
BLOCK
```

Only an ALLOW decision may produce a narrow, short-lived execution capability and an ERC-8196-compatible action envelope for the wallet enforcement layer.

The core security principle is:

```text
MODEL OUTPUT IS A PROPOSAL.
A SIGNATURE IS NOT SEMANTIC SAFETY.
IDENTITY IS NOT AUTHORITY.
REPUTATION IS NOT AUTHORIZATION.
SIMULATION IS EVIDENCE.
EXECUTION REQUIRES DETERMINISTIC VERIFICATION.
```

---

## 2. Why this architecture matters

Ethereum agent standards are rapidly separating identity, verification, reputation and execution. ERC-8004 provides portable agent identity plus reputation and validation registries. ERC-8126 defines agent verification and a risk score. ERC-8196 defines policy-bound AI-agent-authenticated wallet execution and requires verification before agent actions.

AgentShield sits around those primitives. It asks questions that a wallet standard alone cannot answer:

- Did the generated calldata actually implement the user's goal?
- What will the transaction do under the current state?
- Will it create an unlimited token approval?
- Will it transfer an asset to the wrong recipient?
- Did an untrusted webpage causally influence the transaction?
- Did a sub-agent receive authority its parent never had?
- Does the agent's trust tier justify the value at risk?
- Does the action need human review?
- Can we reconstruct the exact causal chain after an incident?

---

## 3. System architecture

```text
                 USER / ASSET OWNER
                        |
                        v
                 NATURAL-LANGUAGE GOAL
                        |
                        v
+-------------------------------------------------------------+
|                         AI AGENT                            |
| planner | DeFi agent | swap agent | portfolio agent        |
+----------------------------+--------------------------------+
                             |
                      Transaction Intent
                             |
                             v
+-------------------------------------------------------------+
|                        AGENTSHIELD                          |
+-------------------------------------------------------------+
| Identity / ERC-8004 adapter                                |
| Reputation + ERC-8126 verification adapter                 |
| Provenance tracker                                         |
| Cryptographically attenuated delegation                    |
| Intent policy compiler                                     |
| Calldata decoder                                           |
| Forked-EVM transaction simulator                           |
| State-diff + asset-flow analyzer                           |
| Contract / MEV risk adapters                               |
| Deterministic policy engine                                |
| Risk engine                                                |
| Human-review gate                                          |
| Flight recorder                                            |
+----------------------------+--------------------------------+
                             |
                  ALLOW / REVIEW / BLOCK
                             |
                             v
+-------------------------------------------------------------+
|                EXECUTION-TIME ENFORCEMENT                   |
| JIT capability | exact tx binding | policy root            |
| ERC-8196 wallet/module | ERC-4337 smart account            |
+----------------------------+--------------------------------+
                             |
                             v
                          ETHEREUM
                             |
                             v
+-------------------------------------------------------------+
|                 FLIGHT RECORDER / SOC                       |
| intent -> provenance -> delegation -> simulation -> verdict |
| -> wallet action -> receipt -> post-state                  |
+-------------------------------------------------------------+
```

---

## 4. Trust boundaries

AgentShield treats the following as different trust domains:

```text
User identity
Agent runtime
Retrieved web/RAG content
MCP/tool output
RPC provider
Simulation infrastructure
Policy service
Human approval service
Smart account
Ethereum consensus
```

A production deployment must not allow the agent runtime to forge policy results, provenance labels, human approvals, or simulation evidence.

---

## 5. Threat model

### 5.1 Prompt injection

A malicious webpage, repository, token metadata page, governance post, email, or tool output instructs the agent to change recipient, approve unlimited allowance, or call another contract.

### 5.2 Intent mismatch

The user asks:

```text
swap 5 ETH to USDC
```

but generated calldata:

```text
approves uint256.max
sends output to attacker
routes through unapproved contract
adds a delegatecall
uses 8 ETH
```

### 5.3 Authority laundering

```text
User -> Portfolio Agent -> DeFi Agent -> Swap Agent
```

A child attempts to obtain `eth:transfer` or a $50,000 ceiling when its parent only delegated `eth:swap` and $2,000.

### 5.4 Malicious or compromised agent

An agent identity can be valid while the current runtime is compromised. Identity therefore does not bypass transaction analysis.

### 5.5 RPC/simulation manipulation

A single RPC or simulator may lie, be stale, or disagree with execution state. High-value production actions should use independently operated simulation/verification paths and state freshness checks.

### 5.6 Replay

A valid approval must not be reusable for a different transaction, target, nonce, policy, chain, or later session.

### 5.7 TOCTOU

State can change between simulation and inclusion. Production enforcement should bind to block/state assumptions where appropriate and revalidate immediately before submission.

---

## 6. Agent identity

`AgentIdentity` separates:

```text
tenant_id
agent_id
agent_address
owner_address
ERC-8004 agent id
reputation
ERC-8126 verification/risk score
validation mechanisms
```

AgentShield does not equate an identity NFT with permission. Identity is an input to policy.

---

## 7. ERC-8004 trust integration

ERC-8004 defines three useful trust primitives:

```text
Identity Registry
Reputation Registry
Validation Registry
```

AgentShield's `identity.py` converts trust signals into a **policy ceiling**, never an unconditional permission.

Example:

```text
NEW agent
reputation 10
verification uncertain
=> low transaction ceiling

ESTABLISHED agent
reputation 90
recent low-risk verification
TEE validation
=> higher possible ceiling
```

A ceiling is still bounded by the owner's explicit delegation and intent.

Formally:

```text
effective_value_limit =
    min(
        owner_policy_limit,
        delegation_chain_limit,
        trust_tier_limit,
        transaction_specific_limit
    )
```

---

## 8. ERC-8126 verification integration

ERC-8126 is modeled as an external trust signal. In a production adapter, AgentShield should retrieve current verification evidence, verify freshness and source, and use it in risk policy.

Important distinction:

```text
verification score != authorization
```

A low-risk agent cannot spend assets the owner never delegated.

---

## 9. Cryptographically attenuated delegation

The security invariant is:

```text
Authority(child) ⊆ Authority(parent)
```

For a chain:

```text
User -> A -> B -> C
```

effective capabilities are the intersection:

```text
C_effective =
    C_user_to_A
  ∩ C_A_to_B
  ∩ C_B_to_C
```

and the effective value ceiling is the minimum of every hop.

The implementation checks:

- continuity of delegator/delegatee
- expiry
- parent digest linkage
- final binding to the executing agent
- capability intersection
- minimum value ceiling

Production should additionally verify EIP-712 signatures or another cryptographic delegation credential at every hop.

---

## 10. Why parent digests matter

Each child delegation should commit to the parent delegation:

```text
D0 = hash(user grant)
D1 = hash(agent A grant + D0)
D2 = hash(agent B grant + D1)
```

This makes the authority path tamper evident.

A production credential should bind:

```text
chain id
tenant
delegator
delegatee
capabilities
resource scope
value ceiling
purpose
valid-after
valid-until
nonce
parent digest
policy version
```

---

## 11. Intent policy

The model may express:

```text
Goal: Convert 5 ETH to USDC
```

The security runtime converts it into explicit invariants:

```text
action             = swap
token_in           = ETH
token_out          = USDC
amount_in          <= 5 ETH
slippage           <= 50 bps
router             in approvedRouters
recipient          = owner
delegatecall       forbidden
new token approval <= required amount
MEV risk           <= threshold
contract risk      <= threshold
```

The natural-language goal itself is not executable authority.

---

## 12. Intent compiler design

A mature deployment should use two stages:

```text
Natural language
      |
      v
Structured intent extraction
      |
      v
Deterministic validation/compiler
      |
      v
Versioned IntentPolicy
```

An LLM may help extract structured fields, but a deterministic compiler must validate types, units, token identities, addresses, chain IDs, and ambiguity.

If the goal is ambiguous, fail to HUMAN_REVIEW rather than guessing.

---

## 13. Transaction decoding

Before execution, decode:

```text
target
selector
function signature
arguments
ETH value
token approvals
permit/Permit2
multicall
delegatecall
internal calls
CREATE/CREATE2
bridge calls
recipient
deadline
slippage/minOut
```

Unknown calldata on a financial path should receive a conservative decision.

---

## 14. Transaction simulation

Simulation is mandatory evidence for execution-grade analysis.

A production simulator should produce:

```text
success/revert
decoded top-level call
internal call tree
logs
state diff
balance diff
allowance diff
asset flows
created contracts
delegatecalls
gas estimate
revert reason
block/state anchor
```

`simulator.py` intentionally exposes a production integration seam. The included deterministic adapter is for tests; `JsonRpcSimulator` refuses to pretend that a simple `eth_call` is a complete security simulation.

Recommended production implementations include:

```text
Anvil fork
reth/Erigon tracing
dedicated simulation cluster
commercial transaction simulation API
```

For high-value actions, compare multiple independent simulations.

---

## 15. State-diff analysis

State diffs often reveal risks hidden by calldata.

Examples:

```text
ERC-20 allowance:
0 -> uint256.max

proxy implementation:
trusted -> unknown

ownership:
owner -> attacker

balance:
vault -1000 USDC
attacker +1000 USDC
```

AgentShield models approvals, storage changes, and balance changes explicitly.

---

## 16. Asset-flow analysis

A transaction should be understood as economic flow, not only ABI calls.

Example expected flow:

```text
Owner --5 ETH--> Router
Router --USDC--> Owner
```

Unexpected flow:

```text
Owner --5 ETH--> Router
Router --USDC--> 0xAttacker
```

This is an intent violation even if the function selector is a valid swap.

---

## 17. Unlimited approval detection

One of the clearest runtime invariants is:

```text
new_approval <= amount required by the intended operation
```

The test suite includes a case where the simulated state diff contains `uint256.max`; the engine blocks it.

Production policy may permit bounded recurring allowances for explicitly approved protocols, but this must be owner policy, not agent discretion.

---

## 18. Delegatecall policy

`delegatecall` can execute code in the caller's storage context. For autonomous financial agents, a default-deny policy is appropriate unless a reviewed smart-account/module architecture explicitly requires it.

The intent policy exposes:

```text
forbid_delegatecall = true
```

---

## 19. Contract risk

Contract risk can combine:

```text
allow/deny lists
code hash
proxy implementation
upgradeability
deployment age
audit/verification status
known exploit intelligence
sanctions/compliance signals where applicable
owner/admin powers
bytecode heuristics
historical incidents
```

No single score should silently authorize execution.

---

## 20. MEV risk

MEV policy can evaluate:

```text
price impact
slippage
sandwich exposure
public-mempool exposure
route complexity
liquidity depth
deadline
private relay availability
```

AgentShield treats MEV risk as one input to the decision.

---

## 21. Provenance tracking

Every influential input should carry provenance:

```text
source
trust label
content hash
parent hashes
security labels
```

Example:

```text
source = https://malicious.example
trust = UNTRUSTED
labels = [indirect-prompt-injection]
```

The provenance root is bound into the policy decision.

---

## 22. Provenance is not authority

This invariant is critical:

```text
retrieved content = context
retrieved content != permission
```

A webpage saying "approve unlimited USDC to this address" cannot create authorization.

---

## 23. Risk-adaptive authorization

AgentShield combines hard gates with risk.

Hard gates should include:

```text
broken delegation
expired delegation
missing capability
value above delegation
forbidden delegatecall
excess approval
simulation failure
blocked contract
recipient mismatch for strict policies
```

Soft/risk evidence may include:

```text
untrusted provenance
new agent
low reputation
moderate contract risk
moderate MEV risk
unusual behavior
novel destination
```

Hard failures are not overridden by reputation.

---

## 24. Decision semantics

### ALLOW

All deterministic invariants pass. A short-lived exact-action capability may be minted.

### HUMAN_REVIEW

The action is not proven malicious, but evidence is ambiguous or risk exceeds autonomous limits.

### BLOCK

A hard invariant failed or risk is unacceptable.

---

## 25. Exact-action binding

An ALLOW decision is bound to the exact transaction digest:

```text
hash(
  chain_id,
  sender,
  target,
  value,
  calldata,
  nonce
)
```

A production version should additionally bind:

```text
state/block anchor
intent hash
delegation root
provenance root
policy version
approval id
expiry
```

Changing calldata invalidates the authorization.

---

## 26. JIT capability token

The reference implementation issues a short-lived signed token after ALLOW.

Claims include:

```text
tenant
agent
owner/on-behalf-of
action
target
max value
transaction hash
delegation root
issued-at
expiry
unique id
```

The reference uses HS256 with the API secret to remain runnable. Production must use asymmetric signing backed by KMS/HSM and publish verification keys.

The capability is an internal enforcement primitive; it is not a replacement for canonical Ethereum signatures or ERC conformance.

---

## 27. ERC-8196 integration

ERC-8196 standardizes policy-bound execution for AI-agent-authenticated wallets. AgentShield prepares an action envelope and policy hash that a canonical ERC-8196 wallet/module integration can consume.

Production flow:

```text
AgentShield ALLOW
       |
       v
Action commitment
       |
       v
Owner policy root / ERC-8196 policy
       |
       v
Agent EIP-712 signature
       |
       v
ERC-8126 verification evidence
       |
       v
ERC-8196 smart account/module
       |
       v
ERC-4337 UserOperation
       |
       v
EntryPoint / Ethereum
```

The Solidity files in this repository are a defense-in-depth integration guard and minimal interface, not a claim of byte-for-byte canonical ERC-8196 conformance.

---

## 28. ERC-4337 integration

A production bundler path should enforce AgentShield at or before UserOperation submission and again at smart-account validation/execution.

Do not rely only on an off-chain API. If the wallet can bypass AgentShield, the security boundary is incomplete.

---

## 29. Execution-time guard

The included `AgentShieldGuard.sol` demonstrates:

```text
approved policy root
approved target
max value
expiry
one-time action digest
replay protection
```

A production account should additionally verify the canonical agent action signature, ERC-8126 evidence, policy fields, nonce semantics, daily limits, revocation, and any owner-specific rules.

---

## 30. Flight recorder

Every important transition should become an immutable/tamper-evident event:

```text
12:41:01 USER_INTENT         swap 5 ETH -> USDC
12:41:03 AGENT_PLAN          use approved router
12:41:04 PROVENANCE          malicious webpage / UNTRUSTED
12:41:06 TX_PROPOSED         router call
12:41:06 SIMULATION          approval uint256.max
12:41:06 INTENT_MISMATCH     approval > required
12:41:07 DECISION            BLOCK
12:41:07 AGENT_STATE         QUARANTINED
```

The current helper produces deterministic event hashes. Production should use an append-only event stream, hash chaining/Merkle checkpoints, signed collectors and immutable/WORM export.

---

## 31. Transaction-level EDR

Authorization answers:

```text
may this agent perform this class of action?
```

EDR asks:

```text
what is this agent doing over time?
has its behavior changed?
what caused this transaction?
is it attempting a dangerous sequence?
```

Example sequence:

```text
untrusted retrieval
 -> new spender
 -> unlimited approval
 -> external transfer
```

A mature AgentShield deployment can consume the same runtime telemetry model as an Agent EDR system and quarantine the agent session after high-confidence compromise.

---

## 32. Quarantine semantics

Quarantine should be enforced outside the agent process:

```text
disable wallet session capability
revoke JIT credentials
block bundler submission
deny high-risk tool calls
disable outbound network if sandboxed
preserve trace
require human reauthorization
```

The current repository returns transaction decisions; actual workload quarantine is an infrastructure integration.

---

## 33. Human approval

High-value or ambiguous actions should produce a review package containing:

```text
human goal
decoded transaction
simulation summary
asset-flow graph
state diff
new approvals
destination reputation
agent trust
delegation path
provenance
risk reasons
exact action hash
expiry
```

The approver must approve the exact action, not a vague session.

---

## 34. Approval integrity

A production approval credential should bind:

```text
approver identity
tenant
agent
intent hash
transaction hash
policy version
simulation block
expiry
decision
```

If anything changes, approval must be invalid.

---

## 35. Multi-agent security

AgentShield treats a multi-agent hierarchy as an authority graph.

Example:

```text
User
  |
  | $50k portfolio scope
  v
Portfolio Agent
  |
  | $10k DeFi scope
  v
DeFi Agent
  |
  | $2k swap-only scope
  v
Swap Agent
```

The final agent can never recover the user's original $50k authority unless every intermediate delegation explicitly preserves it.

---

## 36. Confused deputy defense

A high-privilege supervisor must not execute an action merely because a lower-trust child requests it.

The supervisor must re-check:

```text
principal
delegation
purpose
resource
transaction
provenance
risk
```

at the point of execution.

---

## 37. Cross-agent provenance

Agent-to-agent messages should carry:

```text
origin principal
delegation root
source provenance
trust label
content hash
parent message hashes
```

This prevents an untrusted input from being laundered into "trusted" context simply by passing through another agent.

---

## 38. Replay and nonce safety

Security credentials must be single-use or strongly nonce-bound. The smart-account layer is the final authority for Ethereum nonce semantics; AgentShield adds action-digest replay protection.

---

## 39. Chain separation

Every authorization must bind `chain_id`. A valid decision for a testnet must not authorize mainnet.

Production deployments should also bind smart-account address and verifying contract/domain in EIP-712.

---

## 40. Fail-closed behavior

Execution-grade checks fail closed when:

```text
simulation unavailable
identity unavailable for required policy
verification stale
delegation signature invalid
policy service unavailable
critical risk feed unavailable
state too stale
human approval missing
```

Read-only analysis can degrade more gracefully.

---

## 41. API

### Health

```http
GET /health
```

### Analyze transaction

```http
POST /v1/analyze
X-API-Key: ...
Content-Type: application/json
```

Request contains:

```text
identity
delegation chain
provenance
intent
transaction
simulation evidence
```

Response:

```json
{
  "decision": "ALLOW",
  "risk_score": 2,
  "reasons": [],
  "intent_hash": "0x...",
  "transaction_hash": "0x...",
  "delegation_root": "0x...",
  "provenance_root": "0x...",
  "policy_version": "agentshield-2026-10-04",
  "capability_token": "...",
  "erc8196_action": {
    "agent": "0x...",
    "action": "swap",
    "target": "0x...",
    "value": "5000000000000000000",
    "data": "0x...",
    "policyHash": "0x..."
  }
}
```

---

## 42. Quick start with Docker

Prerequisites:

```text
Docker 24+
Docker Compose v2
curl
```

Run:

```bash
unzip agentshield-ethereum-agent-security-runtime.zip
cd agentshield-ethereum-agent-security-runtime

cp .env.example .env
# Change API_KEY in .env.

docker compose up --build -d
curl http://localhost:8000/health
```

Analyze the example:

```bash
curl -s \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: replace-me' \
  --data @examples/safe-swap.json \
  http://localhost:8000/v1/analyze
```

Stop:

```bash
docker compose down -v
```

---

## 43. Local development

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
uvicorn agentshield.main:app --reload
```

Offline analysis without PostgreSQL:

```bash
agentshield analyze examples/safe-swap.json
```

The CLI invokes the engine directly and therefore does not persist a decision.

---

## 44. Test suite

Run:

```bash
pytest -q
```

Included tests verify:

1. safe, tightly delegated swap is allowed;
2. `uint256.max` approval is blocked;
3. untrusted provenance forces review/block;
4. privilege laundering through a delegation mismatch is blocked.

Production test suites should add ABI fuzzing, property tests, invariant tests, fork tests, ERC-4337 tests, replay tests, malformed EIP-712 signatures, stale simulation, proxy upgrades, malicious token behavior, fee-on-transfer tokens, rebasing tokens, permit/Permit2, multicalls, bridges, flash loans, reentrancy, and adversarial RPC disagreement.

---

## 45. Solidity testing

The repository includes Solidity sources but does not vendor a full Foundry dependency tree.

Recommended:

```bash
cd contracts
forge init --force .
# restore/copy src files if forge init changes the directory
forge build
forge test
```

For a production repository, pin Foundry, OpenZeppelin and account-abstraction dependencies by commit/tag and run Slither, Echidna/Medusa and formal/invariant checks in CI.

---

## 46. Code map

```text
agentshield/config.py
    environment configuration

agentshield/domain.py
    typed security contracts

agentshield/hashing.py
    canonical deterministic hashes

agentshield/identity.py
    reputation/verification -> trust ceiling

agentshield/delegation.py
    non-expanding multi-hop authority

agentshield/provenance.py
    provenance normalization/root

agentshield/intent.py
    intent-to-simulation comparison

agentshield/simulator.py
    simulation interface/integration seam

agentshield/risk.py
    transparent risk aggregation

agentshield/capability.py
    short-lived exact-action capability

agentshield/engine.py
    complete decision pipeline

agentshield/models.py
    durable SQL decision model

agentshield/store.py
    persistence

agentshield/security.py
    local API authentication

agentshield/api.py
    HTTP API

agentshield/flight_recorder.py
    deterministic event hashing

contracts/src/
    wallet integration interfaces/guard

tests/
    security invariants
```

---

## 47. `domain.py`

This is the security vocabulary. Keeping contracts explicit prevents accidental mixing of:

```text
identity
authority
provenance
intent
transaction
simulation
decision
```

Those are different concepts and should remain different types.

---

## 48. `delegation.py`

This module implements the most important multi-agent invariant: authority cannot expand.

It computes capability intersection and the minimum financial ceiling, verifies chain continuity, expiry, parent linkage and final agent binding.

The runnable reference does not verify signatures. That is a production integration item, not something the README hides.

---

## 49. `identity.py`

Trust affects how much autonomy may be granted. It never creates capabilities.

The sample ceiling is deliberately simple and should be replaced with tenant policy.

---

## 50. `intent.py`

This module compares the human/compiled intent with observable simulation results. It checks approved router, amount, recipient, delegatecall, approval amount, MEV risk, contract risk, simulation success and decoded action.

---

## 51. `simulator.py`

This module explicitly refuses to claim that a basic RPC call is a complete transaction simulator.

Production needs traces and state diffs. This design choice prevents a dangerous false sense of security.

---

## 52. `engine.py`

Pipeline:

```text
verify delegation
   |
evaluate provenance
   |
derive trust tier
   |
compare intent to simulation
   |
apply capability/value constraints
   |
score risk
   |
hard gates
   |
ALLOW / REVIEW / BLOCK
   |
mint JIT capability only on ALLOW
```

---

## 53. `capability.py`

The local reference uses JWT HS256 for convenience. Enterprise deployment should use:

```text
KMS/HSM asymmetric signer
key rotation
JWKS/discovery
revocation
short TTL
audience
nonce
single-use consumption
```

---

## 54. SQL persistence

`DecisionRecord` stores:

```text
tenant
agent
transaction hash
intent hash
delegation root
provenance root
decision
risk
reasons
policy version
timestamp
```

Production should add an append-only event ledger, receipt linkage, execution outcome and hash-chain/Merkle evidence.

---

## 55. Database migrations

`create_all()` at startup is a developer convenience.

Production must use Alembic or equivalent migrations with:

```text
expand/contract changes
migration ownership
backward compatibility
rollback strategy
schema version telemetry
```

---

## 56. Redis

Redis is declared as an integration dependency for:

```text
nonce/replay cache
short-lived decision cache
rate limiting
approval session state
revocation
distributed locks
```

The reference core does not pretend Redis is wired where it is not.

---

## 57. Observability

Production metrics should include:

```text
agentshield_decisions_total{decision}
agentshield_analysis_latency_seconds
agentshield_simulation_latency_seconds
agentshield_review_rate
agentshield_block_rate
agentshield_delegation_failures_total
agentshield_intent_mismatches_total
agentshield_untrusted_provenance_total
agentshield_capability_mints_total
agentshield_execution_outcome_total
```

Traces should correlate:

```text
user task
agent run
tool/retrieval trace
transaction proposal
simulation
policy decision
human approval
UserOperation
transaction receipt
```

---

## 58. SLOs

Illustrative—not universal—targets:

```text
policy API availability              99.99%
p95 non-simulation policy latency    < 50 ms
p95 full simulation decision         < 1.5 s
critical hard-gate enforcement       100%
cross-tenant authorization leakage   0
action/receipt trace completeness    100% for high-value actions
```

---

## 59. Deployment topology

```text
Agent Runtime
     |
     v
AgentShield API
     |
     +--> Identity/Trust Adapter
     +--> Provenance Service
     +--> Delegation Verifier
     +--> Intent Compiler
     +--> Simulation Cluster
     +--> Risk Intelligence
     +--> Human Approval
     +--> Capability Signer
     |
     v
Bundler / Wallet PEP
     |
     v
ERC-4337 / ERC-8196 account
     |
     v
Ethereum
```

---

## 60. Kubernetes

The included deployment is a starter. Production should add:

```text
Service
Ingress/API gateway
HPA
PDB
topology spread
NetworkPolicy
workload identity
managed secrets
resource requests/limits
Pod Security admission
image signing/verification
mTLS/service mesh if appropriate
OTel collector
separate simulation workers
separate signer service
```

The signing key should never be an environment variable in a real high-value deployment.

---

## 61. High availability

Stateless analysis workers scale horizontally. Stateful components require separate HA design:

```text
PostgreSQL -> managed HA / multi-AZ
Redis -> clustered/managed
simulation -> worker pool
policy -> versioned replicas
KMS/HSM -> regional redundancy
event bus -> replicated
audit archive -> immutable storage
```

---

## 62. Multi-region

Do not blindly active-active a financial authorization system.

Define:

```text
policy source of truth
revocation propagation
nonce ownership
regional signer policy
chain RPC locality
data residency
approval locality
failover semantics
```

A safe degraded mode may be "review/block writes, allow read-only analysis."

---

## 63. Event-driven architecture

At scale:

```text
TransactionProposed
SimulationCompleted
PolicyEvaluated
HumanReviewRequested
HumanReviewCompleted
CapabilityMinted
UserOperationSubmitted
TransactionMined
ExecutionReverted
AgentQuarantined
CredentialRevoked
```

Use an outbox pattern for durable publication rather than dual-writing SQL and a broker.

---

## 64. Idempotency

A financial authorization endpoint should accept an idempotency key and persist request/result mapping.

Never assume a timeout means the operation did not happen.

---

## 65. UNKNOWN execution state

If submission times out:

```text
do not blindly retry
```

State becomes:

```text
UNKNOWN
```

Reconcile by:

```text
UserOperation hash
transaction hash
account nonce
EntryPoint events
receipt
state diff
```

Only then retry.

---

## 66. Policy versioning

Every verdict records a policy version.

A production system should support:

```text
draft
shadow
canary
active
deprecated
revoked
```

Never silently change the semantics of an old decision.

---

## 67. Shadow mode

New policies should run without enforcement first:

```text
current policy -> actual decision
candidate policy -> shadow decision
```

Measure divergence and false positives before activation.

---

## 68. Emergency controls

Provide independent kill paths:

```text
owner revokes agent
owner revokes policy
wallet disables module/session key
bundler denies agent
credential signer revokes capability
sandbox quarantines workload
```

No single AI agent should control its own kill switch.

---

## 69. Security of the security system

AgentShield itself is a high-value target.

Protect:

```text
policy admin
signer
simulator
identity adapters
approval UI
RPC credentials
audit store
deployment pipeline
```

Use least privilege, workload identity, mTLS where justified, signed releases, dependency scanning, secret scanning and isolated signer infrastructure.

---

## 70. Applications

### DeFi swap agents

Verify token pair, amount, router, slippage, recipient, approvals, price impact and MEV exposure.

### Portfolio rebalancing agents

Bound total value, asset universe, daily turnover, venue allowlist and concentration limits.

### Treasury agents

Require multi-person approval for high value, restrict destinations and bind execution to accounting policy.

### DAO agents

Constrain governance execution, treasury transfers and contract upgrades.

### NFT agents

Restrict marketplace, collection, maximum bid, royalty/payment flow and approvals.

### Bridge agents

Validate source/destination chain, canonical bridge, recipient, token, minimum received and bridge risk.

### Payment agents

Use per-merchant/per-day ceilings, recipient allowlists and purpose-bound delegation.

### Smart-contract maintenance agents

Restrict upgrade/admin operations to reviewed bytecode hashes and mandatory human approval.

---

## 71. Example: safe swap

```text
Goal
  Convert 5 ETH to USDC

Delegation
  eth:swap
  <= 5 ETH
  valid for 1 hour

Simulation
  approved router
  no delegatecall
  output -> owner
  no excessive approval
  low MEV risk
  low contract risk

Decision
  ALLOW
```

---

## 72. Example: indirect prompt injection

```text
User asks for a swap
        |
Agent reads token webpage
        |
Webpage contains hidden instruction
        |
Agent proposes uint256.max approval
        |
Simulation exposes allowance diff
        |
Intent policy rejects approval
        |
BLOCK
        |
session may be quarantined
```

The security decision does not require perfect prompt-injection classification; transaction semantics provide an independent defense.

---

## 73. Example: authority laundering

```text
User -> Portfolio Agent: eth:swap <= $10k
Portfolio -> DeFi Agent: eth:swap <= $2k
DeFi Agent -> Swap Agent: eth:transfer <= $50k
```

The final grant cannot manufacture `eth:transfer` or increase value. Intersection/minimum semantics deny it.

---

## 74. Example: malicious router

Even if calldata says `swap`, simulation may reveal:

```text
unexpected transfer
new approval
wrong recipient
proxy upgrade
delegatecall
```

AgentShield reasons over effects, not just function names.

---

## 75. Example: trust-adaptive autonomy

A low-reputation/new agent may be allowed to autonomously execute small swaps while larger actions require review.

An established agent can receive a larger ceiling only if the owner explicitly delegates it.

---

## 76. Integration with an Agent EDR

AgentShield pairs naturally with a runtime EDR:

```text
AgentShield
  pre-execution semantic/financial authorization

Agent EDR
  continuous behavioral monitoring

Wallet guard
  deterministic execution enforcement

SOC
  incident investigation/remediation
```

---

## 77. Integration with RAG security

RAG provenance can feed AgentShield:

```text
retrieved document
 -> provenance label
 -> agent reasoning context
 -> proposed transaction
 -> AgentShield risk
```

But provenance is never permission.

---

## 78. Integration with MCP

MCP tools that submit or prepare transactions should terminate at a gateway/PEP that requires an AgentShield decision.

Tool discovery answers:

```text
what tool can do this?
```

AgentShield answers:

```text
may this exact transaction execute?
```

---

## 79. Data model evolution

Production entities likely include:

```text
Principal
Agent
AgentIdentity
Verification
ReputationSnapshot
Delegation
Intent
Policy
TransactionProposal
Simulation
StateDiff
AssetFlow
Decision
Approval
Capability
UserOperation
Receipt
Incident
FlightRecorderEvent
```

---

## 80. Audit graph

A mature audit graph should link:

```text
User
 -> Intent
 -> Agent
 -> Delegation
 -> Provenance
 -> TransactionProposal
 -> Simulation
 -> Decision
 -> HumanApproval?
 -> Capability
 -> UserOperation
 -> Transaction
 -> Receipt
 -> StateDiff
```

This answers:

> Why did this agent have authority to cause this exact on-chain effect?

---

## 81. Evidence integrity

Hashing alone is not enough if an attacker can rewrite the whole database.

Production evidence should combine:

```text
signed collectors
append-only storage
hash chaining
periodic Merkle roots
external timestamp/anchor
WORM archive
SIEM export
restricted evidence administration
```

---

## 82. Privacy

Do not put sensitive prompts or proprietary policy text on-chain.

Prefer commitments/hashes and keep detailed evidence in access-controlled off-chain storage.

---

## 83. Rate limits and abuse controls

Protect expensive simulation and trust adapters with:

```text
tenant quotas
agent quotas
concurrency limits
cost budgets
RPC budgets
circuit breakers
bulkheads
```

---

## 84. Circuit breakers

Trip on:

```text
RPC disagreement
simulator failure spike
chain reorg instability
risk feed outage
abnormal block rate
capability signer anomaly
mass approval attempts
```

Financial autonomy should degrade conservatively.

---

## 85. Chain reorgs

Do not treat a receipt as final immediately. Finality policy depends on chain and value at risk.

Flight recorder state should distinguish:

```text
submitted
included
confirmed
finalized
reorged
```

---

## 86. Proxy contracts

Policy should resolve proxy implementation and record:

```text
proxy address
implementation address
implementation code hash
upgrade admin
upgradeability model
```

A target allowlist without implementation awareness is insufficient.

---

## 87. Token edge cases

Simulation/evaluation must consider:

```text
fee-on-transfer
rebasing
ERC-777 hooks
non-standard ERC-20 returns
blacklists/pauses
permit
Permit2
tax tokens
honeypots
```

---

## 88. Multicall

A top-level approved router may hide dangerous nested calls.

Policy must inspect the full internal call tree and aggregate economic effects.

---

## 89. Bridges

Cross-chain execution needs two-sided reasoning:

```text
source-chain lock/burn
message/bridge
destination-chain mint/release
```

Authorization should bind destination chain and recipient.

---

## 90. Account abstraction concerns

ERC-4337 adds:

```text
UserOperation
EntryPoint
bundler
paymaster
account validation
```

AgentShield should record and policy-check paymaster/bundler behavior when relevant.

---

## 91. Paymaster policy

A malicious or unexpected paymaster can add dependencies or fail execution. High-value deployments should allowlist or validate paymasters.

---

## 92. Session keys

Session keys are a natural enforcement mechanism for agent autonomy when tightly scoped by:

```text
target
selector
value
time
nonce
spend
chain
```

AgentShield's capability model maps well to session-key architectures.

---

## 93. Daily limits

Daily spend cannot be safely implemented only in a stateless API.

Production needs durable, race-safe accounting at the wallet/module or a strongly consistent policy service, with on-chain enforcement preferred for critical limits.

---

## 94. Reputation manipulation

Reputation is attackable through sybil behavior, collusion and stale signals.

Therefore:

```text
reputation changes risk/autonomy
reputation never bypasses hard policy
```

---

## 95. Validation mechanisms

ERC-8004 permits pluggable validation. AgentShield can consume attestations from:

```text
stake-secured re-execution
zkML
TEE
trusted judges
other validators
```

Policy should record who validated, what was validated, freshness and evidence.

---

## 96. Model upgrades

Changing the LLM can change behavior.

Record:

```text
model/provider
agent build
prompt/policy version
tool versions
retrieval version
```

for high-value sessions.

---

## 97. Safe reasoning telemetry

Do not depend on hidden chain-of-thought.

Record observable security metadata:

```text
task
structured intent
tool requests
retrieval provenance
transaction proposals
simulation
policy results
approvals
execution outcomes
```

---

## 98. Red-team strategy

Test:

```text
indirect prompt injection
malicious token metadata
malicious router
malicious RPC
unlimited approval
wrong recipient
delegatecall
proxy upgrade
permit abuse
multicall hiding
bridge redirection
delegation escalation
replay
stale simulation
reorg
human-approval substitution
cross-tenant request
```

---

## 99. Property-based invariants

Examples:

```text
child authority never exceeds parent
BLOCK never mints capability
ALLOW requires successful simulation
changing calldata changes tx hash
changing delegation changes root
expired delegation never allows
forbidden delegatecall never allows
approval above intent never allows
```

These should be property-tested, not only example-tested.

---

## 100. Fuzzing

Fuzz ABI/calldata decoders and policy boundaries.

Useful targets:

```text
nested multicall
malformed dynamic ABI
huge arrays
unknown selectors
proxy fallback
token return anomalies
permit signatures
edge timestamps
value overflow boundaries
```

---

## 101. Formal verification candidates

Smart-contract invariants are good candidates for formal methods:

```text
no replay
policy root required
target allowlist enforced
value limit enforced
expiry enforced
owner-only policy mutation
```

---

## 102. CI/CD

A production pipeline should run:

```text
Python unit/integration tests
ruff/type checking
Solidity build/tests
Slither
fuzz/invariant tests
dependency audit
SBOM
secret scan
container scan
image signing
IaC policy
staging fork tests
shadow-policy replay
```

---

## 103. Release management

Security policy, contracts and services should be independently versioned.

A release record should identify:

```text
git commit
container digest
contract bytecode hash
policy bundle hash
migration version
detector version
simulator version
```

---

## 104. Incident response

If AgentShield detects a critical event:

```text
1 block exact transaction
2 revoke JIT capability
3 quarantine agent session
4 stop wallet/bundler route
5 preserve flight recorder
6 rotate exposed credentials if needed
7 identify provenance root
8 inspect sibling/sub-agent activity
9 review on-chain pending actions
10 update policy/detection
11 replay historical traces
12 human-authorize recovery
```

---

## 105. Principal-engineer design review questions

1. Where is the actual enforcement point?
2. Can the agent bypass the API?
3. How is tenant identity derived?
4. How are delegation signatures verified?
5. How is authority attenuation proven?
6. How fresh is ERC-8126 evidence?
7. Can reputation override policy?
8. How are proxy upgrades handled?
9. What happens when simulators disagree?
10. What state is simulation anchored to?
11. How is TOCTOU reduced?
12. How is a human approval bound to calldata?
13. How are daily limits race-safe?
14. What happens on RPC outage?
15. What happens after submission timeout?
16. How is evidence made tamper evident?
17. How are policy versions rolled out?
18. How are contracts fuzzed/formally checked?
19. What is the safe degraded mode?
20. How are agent/runtime compromises contained?

---

## 106. Production readiness matrix

| Area | Runnable reference | Enterprise production target |
|---|---|---|
| Typed API | Yes | Versioned API + authn/z |
| Intent checks | Yes | Full compiler + ABI semantics |
| Simulation model | Yes | Multi-simulator forked EVM |
| State diff | Data model | Real trace/state extraction |
| Asset flow | Data model/checks | Full token/native/NFT graph |
| Delegation | Intersection/link checks | Signed EIP-712 credentials |
| Provenance | Hash root | Signed provenance graph |
| ERC-8004 | Data model | On-chain registry adapter |
| ERC-8126 | Data model | Live verified adapter |
| ERC-8196 | Envelope + guard seam | Canonical conformant wallet/module |
| ERC-4337 | Architecture | Bundler/account integration |
| JIT capability | HS256 reference | KMS/HSM asymmetric |
| Persistence | PostgreSQL | Migrations + HA |
| Replay | Action digest | Distributed nonce/revocation |
| Flight recorder | Hash helper | Event bus + immutable evidence |
| Human review | Decision state | SSO/SoD/M-of-N |
| Quarantine | Architecture | Runtime/bundler/wallet enforcement |
| Observability | Specified | OTel/Prometheus/SIEM |
| K8s | Starter | Helm/HPA/PDB/NetworkPolicy |
| Tests | Core invariants | fork/fuzz/property/load/red-team |

---

## 107. What is genuinely implemented

The repository contains runnable source for:

```text
typed agent/intent/transaction/simulation contracts
multi-hop delegation intersection
delegation continuity/expiry/parent linkage
provenance hashing
trust-tier calculation
intent-vs-simulation checks
approval-limit checks
delegatecall checks
router/recipient/value checks
MEV/contract risk inputs
risk aggregation
ALLOW / HUMAN_REVIEW / BLOCK
short-lived exact-action capability
ERC-8196 action envelope
SQL decision persistence
FastAPI service
offline CLI
flight-recorder event hashing
Solidity execution guard
Docker Compose
Kubernetes starter
unit tests
```

---

## 108. What remains deployment-specific

Calling this repository a complete bank-grade production deployment without these integrations would be misleading:

```text
production OIDC/workload identity
live ERC-8004 registry adapter
live ERC-8126 verification adapter
canonical ERC-8196 wallet/module
full ERC-4337 bundler integration
EIP-712 signed delegation service
real forked-EVM simulator
ABI/internal-call decoder
state-diff extractor
complete asset-flow engine
MEV provider
contract threat intelligence
DLP/prompt-injection telemetry
SSO human approval
KMS/HSM signer
revocation service
actual quarantine/kill integration
event bus/outbox
immutable evidence store
Alembic migrations
Redis nonce/replay implementation
OTel/Prometheus wiring
SIEM/SOAR export
multi-region controls
large fork/fuzz/formal test suite
external smart-contract audit
```

The architecture defines where those components connect; the runnable core demonstrates the critical security semantics without pretending external infrastructure exists.

---

## 109. Recommended production implementation order

```text
Phase 1  OIDC/workload identity + trusted tenant
Phase 2  EIP-712 signed delegation credentials
Phase 3  live ERC-8004/8126 adapters
Phase 4  forked-EVM simulation + ABI/call-tree/state diff
Phase 5  full asset-flow/approval/proxy analysis
Phase 6  policy bundle service + shadow/canary
Phase 7  KMS capability signer + revocation
Phase 8  SSO human approval
Phase 9  ERC-8196/4337 wallet enforcement
Phase 10 event bus + immutable flight recorder
Phase 11 quarantine/bundler/network enforcement
Phase 12 OTel/SIEM + red-team/fuzz/formal gates
Phase 13 HA/multi-region/residency
```

---

## 110. Suggested production service split

```text
identity-service
delegation-service
provenance-service
intent-service
simulation-service
asset-flow-service
policy-service
risk-service
approval-service
capability-signer
wallet-gateway
flight-recorder
incident-service
```

Start as a modular monolith unless scale/ownership requires separation. Premature microservices make security transactions harder to reason about.

---

## 111. Why Python plus Solidity

Python is appropriate for:

```text
agent integrations
policy orchestration
simulation adapters
security analytics
risk intelligence
SOC/evaluation
rapid protocol integration
```

Solidity is required for the final on-chain enforcement boundary.

For very high-throughput infrastructure, Go/Rust are strong choices for:

```text
RPC gateway
bundler PEP
simulation workers
event collectors
stream processors
signing proxy
```

The architecture is language-neutral.

---

## 112. Relationship to a Zero-Trust agent control plane

```text
Zero-Trust agent control plane
  identity + delegation + provenance + authorization

AgentShield
  Ethereum intent + transaction semantics + wallet enforcement

Agent EDR
  continuous behavior + containment

Together
  preventive + transaction-aware + detective security
```

---

## 113. Relationship to traditional wallet simulation

Wallet simulation usually answers:

```text
what will this transaction do?
```

AgentShield additionally asks:

```text
why is the agent doing it?
who delegated authority?
what was the user's intent?
what untrusted content influenced it?
does the economic effect match the goal?
should autonomy be allowed for this trust/risk tier?
```

---

## 114. Research novelty

Interesting research directions include:

```text
cryptographically attenuated multi-agent delegation
intent-to-state-diff verification
provenance-conditioned financial authorization
risk-adaptive agent autonomy
cross-agent authority-laundering detection
causal transaction flight recorders
counterfactual transaction replay
proof-carrying agent execution
```

The strongest unifying concept is:

```text
probabilistic planning
        |
        v
structured intent
        |
        v
cryptographic authority
        |
        v
deterministic simulation/policy
        |
        v
exact-action proof
        |
        v
on-chain enforcement
```

---

## 115. Public standards references

1. **ERC-8196 — AI Agent Authenticated Wallet**  
   Canonical EIP: https://eips.ethereum.org/EIPS/eip-8196  
   Used as the public reference for policy-bound AI-agent wallet execution, agent action/delegation structures, verification integration and tamper-evident audit concepts.

2. **ERC-8004 — Trustless Agents**  
   Canonical EIP: https://eips.ethereum.org/EIPS/eip-8004  
   Used as the public reference for portable agent identity, reputation feedback and validation registries.

3. **ERC-8126 — AI Agent Verification**  
   Canonical EIP: https://eips.ethereum.org/EIPS/eip-8126  
   Used as the public reference for agent verification and risk evidence consumed by ERC-8196.

4. **ERC-4337 — Account Abstraction Using Alt Mempool**  
   Canonical EIP: https://eips.ethereum.org/EIPS/eip-4337  
   Used as the account-abstraction execution context.

These references establish interoperability context. AgentShield is an independent architecture and does not claim endorsement, canonical conformance beyond what is explicitly tested, or reproduction of any private implementation.

---

## 116. Final security invariant

```text
AN AGENT MAY PROPOSE.
IT MAY NOT SELF-AUTHORIZE.

Before financial execution, independently verify:

identity
+ delegated authority
+ provenance
+ structured intent
+ decoded transaction
+ simulation
+ state diff
+ asset flow
+ contract/MEV risk
+ policy
+ human approval when required
+ exact-action binding
+ on-chain enforcement.
```

That boundary is the purpose of AgentShield.
---

# Part II — Complete Operator, Developer, Security and Deployment Handbook

This section turns the repository README into a self-contained engineering handbook for building, running, evaluating and extending AgentShield.

## 117. End-to-end lifecycle

The complete lifecycle of an autonomous Ethereum action is:

```text
1. User authenticates
2. User supplies a financial goal
3. Agent creates a structured intent
4. Agent gathers external context
5. Every influential input receives provenance
6. Agent proposes a transaction
7. Delegation chain is reconstructed
8. Agent identity/trust evidence is resolved
9. Calldata is decoded
10. Transaction is simulated against anchored chain state
11. Internal calls, logs, approvals and state diffs are extracted
12. Asset flows are reconstructed
13. Intent invariants are compared with simulated effects
14. Contract and MEV risk are evaluated
15. Deterministic hard gates run
16. Risk policy chooses ALLOW / HUMAN_REVIEW / BLOCK
17. ALLOW produces exact-action capability
18. Review produces exact-action approval request
19. Wallet enforcement verifies proof/policy
20. ERC-4337 UserOperation is submitted
21. Receipt and post-state are reconciled
22. Flight Recorder links cause -> decision -> execution
23. EDR continues observing the agent
```

The important architectural property is that steps 7–19 occur outside the probabilistic agent.

## 118. Component interaction sequence

```text
User        Agent      AgentShield       Simulator       Approval       Wallet        Ethereum
 |            |             |                |               |             |              |
 |--goal----->|             |                |               |             |              |
 |            |--intent---->|                |               |             |              |
 |            |--tx-------->|                |               |             |              |
 |            |             |--simulate----->|               |             |              |
 |            |             |<--state diff---|               |             |              |
 |            |             |--policy/risk-->|               |             |              |
 |            |             |                |               |             |              |
 |            |             |--REVIEW----------------------->|             |              |
 |<--------------------------------review UI------------------|             |              |
 |------------------------------exact approval-------------->|             |              |
 |            |             |<--approval---------------------|             |              |
 |            |             |--capability-------------------------------->|              |
 |            |             |                                             |--UserOp----->|
 |            |             |                                             |<--receipt-----|
 |            |             |<----------------receipt/reconciliation-------|              |
```

## 119. Repository tree

```text
agentshield-ethereum-agent-security-runtime/
├── README.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── agentshield/
│   ├── __init__.py
│   ├── api.py
│   ├── capability.py
│   ├── cli.py
│   ├── config.py
│   ├── db.py
│   ├── delegation.py
│   ├── domain.py
│   ├── engine.py
│   ├── flight_recorder.py
│   ├── hashing.py
│   ├── identity.py
│   ├── intent.py
│   ├── main.py
│   ├── models.py
│   ├── provenance.py
│   ├── risk.py
│   ├── security.py
│   ├── simulator.py
│   └── store.py
├── contracts/
│   └── src/
│       ├── IAIAgentAuthenticatedWallet.sol
│       └── AgentShieldGuard.sol
├── deploy/
│   └── k8s/
│       └── deployment.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INTEGRATIONS.md
│   ├── PRODUCTION_READINESS.md
│   ├── RUNBOOK.md
│   ├── SECURITY_INVARIANTS.md
│   └── THREAT_MODEL.md
├── examples/
│   └── safe-swap.json
└── tests/
    └── test_engine.py
```

## 120. Configuration reference

The reference service is configured through environment variables.

| Variable | Meaning | Production guidance |
|---|---|---|
| `API_KEY` | Local API authentication secret | Replace with OIDC/workload identity |
| `DATABASE_URL` | Async PostgreSQL DSN | Managed HA database + TLS |
| `REDIS_URL` | Redis endpoint | Managed Redis with auth/TLS |
| `CHAIN_ID` | Ethereum chain identifier | Bind every decision to chain |
| `RPC_URL` | Ethereum RPC | Use authenticated, redundant providers |
| `HUMAN_REVIEW_THRESHOLD` | Risk threshold for review | Version as policy |
| `BLOCK_THRESHOLD` | Risk threshold for blocking | Version as policy |
| `MAX_DELEGATION_DEPTH` | Maximum delegation hops | Keep deliberately small |
| `CAPABILITY_TTL_SECONDS` | JIT capability lifetime | Prefer minutes, not hours |
| `POLICY_VERSION` | Decision policy version | Immutable release identifier |

## 121. First run — Docker Compose

```bash
unzip agentshield-ethereum-agent-security-runtime-comprehensive.zip
cd agentshield-ethereum-agent-security-runtime

cp .env.example .env
```

Set a strong local development API key:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

Put the generated value in `.env`:

```text
API_KEY=<generated-value>
```

Start the stack:

```bash
docker compose up --build -d
```

Inspect status:

```bash
docker compose ps
```

Check health:

```bash
curl -s http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

## 122. Send the safe-swap example

If the `.env` key is `replace-me`:

```bash
curl -s \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: replace-me' \
  --data @examples/safe-swap.json \
  http://localhost:8000/v1/analyze
```

An allowed response contains:

```text
decision = ALLOW
capability_token != null
erc8196_action != null
```

## 123. Inspect service logs

```bash
docker compose logs -f api
```

PostgreSQL:

```bash
docker compose logs -f postgres
```

Redis:

```bash
docker compose logs -f redis
```

## 124. Stop or reset the environment

Stop containers while retaining volumes:

```bash
docker compose stop
```

Restart:

```bash
docker compose start
```

Remove containers:

```bash
docker compose down
```

Remove containers and development volumes:

```bash
docker compose down -v
```

Never run the destructive `-v` form against an environment whose data must be retained.

## 125. Native Python run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run tests:

```bash
pytest -q
```

Start API:

```bash
uvicorn agentshield.main:app --host 0.0.0.0 --port 8000 --reload
```

## 126. Offline CLI

The CLI bypasses HTTP and persistence and directly exercises the security engine:

```bash
agentshield analyze examples/safe-swap.json
```

This is useful for:

```text
CI security checks
policy regression
attack corpus replay
developer debugging
red-team automation
```

## 127. API authentication model

The runnable API uses an API key so the repository works without an external IdP.

Production replacement:

```text
Enterprise IdP
     |
     v
OIDC access token
     |
     v
API Gateway
     |
     v
JWT validation
     |
     +-- tenant claim
     +-- user principal
     +-- roles
     +-- authorization context
     |
     v
AgentShield
```

Never trust a caller-supplied tenant identifier without binding it to authenticated identity.

## 128. Database operation

The service creates the reference schema on startup. This is convenient locally but unsuitable for controlled production migrations.

Production:

```text
Git release
   |
Alembic migration
   |
staging validation
   |
expand migration
   |
application rollout
   |
contract migration
```

Database backups should be encrypted, regularly restored in tests, and subject to retention policy.

## 129. Decision persistence

Each persisted decision includes enough immutable identifiers to answer:

```text
which tenant?
which agent?
which transaction?
which intent?
which delegation graph?
which provenance graph?
which policy?
which decision?
which risk score?
when?
```

Execution receipts should be added in production so authorization and actual on-chain effects can be compared.

## 130. Recommended production SQL additions

Add tables for:

```text
agent_identity_snapshot
verification_snapshot
delegation
delegation_signature
intent
transaction_proposal
simulation
internal_call
state_diff
asset_flow
approval_request
approval_decision
capability
user_operation
transaction_receipt
flight_event
incident
policy_bundle
revocation
outbox_event
```

## 131. Redis usage

Recommended Redis keys:

```text
nonce:{tenant}:{agent}
revocation:{jti}
decision:{tx_hash}
approval:{approval_id}
rate:{tenant}:{agent}
lock:{wallet}:{nonce}
```

Redis must not become the sole durable source of financial truth.

## 132. Simulation cluster

Production topology:

```text
                  Simulation API
                       |
          +------------+------------+
          |                         |
     Worker Pool A               Worker Pool B
          |                         |
       reth fork                  Anvil fork
          |                         |
          +------------+------------+
                       |
                 Result Comparator
                       |
                  State/Call Graph
```

High-value policy may require quorum or agreement between independent simulation engines.

## 133. Simulation freshness

Record:

```text
chain_id
block_number
block_hash
state_root where available
RPC provider
simulator build
simulation timestamp
```

A policy may reject a decision if too many blocks have elapsed before submission.

## 134. Calldata decoder

The production decoder should support:

```text
verified ABI
selector database
proxy implementation ABI
multicall recursion
fallback calls
Permit
Permit2
ERC-20
ERC-721
ERC-1155
common DEX routers
bridges
ERC-4337 account calls
```

Unknown selectors should increase risk or require review.

## 135. Economic graph

Convert execution traces into:

```text
Node:
  account / token / contract

Edge:
  transfer / approve / mint / burn / stake / borrow / repay
```

Then compare the graph with the intent.

This is more robust than comparing only function names.

## 136. Intent compiler failure modes

The compiler must detect ambiguity such as:

```text
"buy some ETH"
"send it to my wallet"
"use the best bridge"
"swap at a reasonable price"
```

Ambiguity should become:

```text
NEEDS_CLARIFICATION
```

before financial execution.

## 137. Policy compiler

Example owner policy:

```yaml
version: treasury-2026-10
chains:
  - 1
allowed_actions:
  - swap
allowed_routers:
  - "0x..."
max_value_per_tx_wei: "5000000000000000000"
max_daily_value_wei: "10000000000000000000"
max_slippage_bps: 50
delegatecall: deny
unlimited_approval: deny
unknown_contract: review
untrusted_provenance_write: review
```

The production compiler should convert this into deterministic policy data, not prompt text.

## 138. Policy precedence

Recommended precedence:

```text
Emergency deny
   >
Regulatory/enterprise policy
   >
Owner policy
   >
Delegation constraints
   >
Transaction-specific intent
   >
Risk/autonomy policy
```

Lower layers can narrow authority; they cannot widen higher-layer constraints.

## 139. Risk engine design

Do not reduce all security to a score.

Use:

```text
hard deterministic gates
+
risk evidence
+
review threshold
```

A forbidden target remains forbidden even if the agent has reputation 100.

## 140. Risk explainability

Every risk increment should produce:

```text
rule id
severity
evidence id
human explanation
policy version
```

This supports audits and SOC investigation.

## 141. Human review UX

A useful review screen should show:

```text
User goal
Agent
Trust/reputation
Delegation chain
Target contract
Decoded method
Value
Token approvals
Asset-flow before/after
Simulation block
Contract risk
MEV risk
Untrusted provenance
Risk reasons
Exact action digest
```

Avoid an approval button that says only "Allow agent."

## 142. Separation of duties

Examples:

```text
< $1k       autonomous if policy passes
$1k-$10k    one human approver
$10k-$100k  two independent approvers
admin op    security + asset owner
```

Exact thresholds are organization policy.

## 143. Capability consumption

A production capability should be:

```text
short lived
single use
audience bound
agent bound
wallet bound
chain bound
transaction bound
policy bound
revocable
```

## 144. Signer isolation

Recommended:

```text
AgentShield API
      |
      v
Capability Signer Service
      |
      v
KMS/HSM
```

The API never receives raw private key material.

## 145. Wallet enforcement point

The critical rule is:

```text
If the wallet can execute around AgentShield,
AgentShield is not an enforcement system.
```

Wallet/module validation must independently verify the required proof/commitment.

## 146. ERC-4337 path

```text
Agent
  |
AgentShield
  |
Smart-account callData
  |
UserOperation
  |
Bundler validation/simulation
  |
EntryPoint
  |
Account validation
  |
Account execution
  |
Target protocol
```

AgentShield complements rather than replaces ERC-4337 validation.

## 147. Bundler PEP

A controlled bundler can provide an additional enforcement point:

```text
reject revoked agent
reject stale policy
reject missing capability
reject quarantined session
reject stale simulation
```

The smart account remains the stronger final boundary.

## 148. ERC-8004 adapter

Production adapter responsibilities:

```text
resolve agent ID
read owner/operator
resolve registration metadata
read reputation feedback
read validation requests/responses
record block number
record finality
cache safely
detect registry/network mismatch
```

## 149. Reputation policy

Use reputation as an autonomy modifier.

Bad:

```text
reputation > 80 => bypass checks
```

Good:

```text
reputation > 80
AND all deterministic checks pass
AND explicit owner delegation exists
=> eligible for higher autonomous ceiling
```

## 150. ERC-8126 adapter

Record:

```text
agent id
verification type
provider
risk score
evidence reference
verification timestamp
block/attestation reference
freshness
```

Policy should define maximum evidence age.

## 151. Provenance graph

A production provenance graph might look like:

```text
User Goal
   |
   +--> Trusted enterprise policy
   |
   +--> Web page [UNTRUSTED]
              |
              v
         Agent plan
              |
              v
       Transaction proposal
```

If an untrusted node causally controls a dangerous field, review/block policy can react.

## 152. Field-level provenance

Prefer:

```text
target_address <- protocol registry
recipient      <- authenticated owner profile
amount         <- user instruction
router         <- route optimizer
slippage       <- owner policy
```

over one coarse label for the entire prompt.

## 153. Transaction EDR

Useful behavioral detections:

```text
new spender + unlimited approval
new contract + high value
untrusted retrieval + approval
repeated blocked transactions
rapid value escalation
new bridge destination
new chain
proxy implementation changed
agent attempts policy-admin tool
```

## 154. Flight Recorder schema

Recommended event:

```json
{
  "event_id": "...",
  "tenant": "...",
  "session": "...",
  "agent": "...",
  "timestamp": "...",
  "kind": "SIMULATION_COMPLETED",
  "parents": ["..."],
  "payload_hash": "0x...",
  "policy_version": "...",
  "agent_build": "...",
  "collector_identity": "...",
  "signature": "..."
}
```

## 155. Flight Recorder replay

A mature CLI should support:

```bash
agentshield replay <session-id>
agentshield graph <session-id>
agentshield explain <transaction-hash>
```

Expected reconstruction:

```text
user intent
 -> retrieval
 -> agent proposal
 -> delegation
 -> simulation
 -> mismatch
 -> decision
 -> approval?
 -> submission?
 -> receipt?
```

## 156. Incident classification

Useful categories:

```text
PROMPT_INJECTION
AUTHORITY_ESCALATION
INTENT_MISMATCH
UNLIMITED_APPROVAL
MALICIOUS_TARGET
WRONG_RECIPIENT
DELEGATECALL
SIMULATION_DIVERGENCE
RPC_INTEGRITY
REPLAY
CREDENTIAL_COMPROMISE
POLICY_TAMPERING
```

## 157. Quarantine state machine

```text
ACTIVE
  |
  +--> RESTRICTED
  |
  +--> QUARANTINED
            |
            +--> INVESTIGATING
                      |
                      +--> RELEASED
                      |
                      +--> TERMINATED
```

A quarantined agent must not mint new financial capabilities.

## 158. Recovery

Release requires:

```text
incident resolved
credentials rotated if needed
pending operations reconciled
policy updated
human authorization
new clean agent/runtime session
```

## 159. Contract deployment

The included Solidity guard is an integration reference.

For local contract development:

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Then create/pin a Foundry workspace and copy the repository Solidity sources into it.

Production requirements include:

```text
pinned compiler
optimizer settings
deterministic deployment
verified source
bytecode hash recording
independent audit
Slither
fuzzing
invariant tests
formal checks for critical properties
```

## 160. Solidity invariants

At minimum:

```text
only owner mutates policy
unapproved policy never executes
unapproved target never executes
value limit cannot be bypassed
expired action never executes
action digest cannot be consumed twice
chain/domain separation holds
```

## 161. CI pipeline

Recommended stages:

```text
checkout
 -> dependency lock verification
 -> Python lint/type checks
 -> Python unit tests
 -> contract build
 -> Solidity unit tests
 -> Slither
 -> fuzz/invariant tests
 -> dependency audit
 -> secret scan
 -> SBOM
 -> container build
 -> container scan
 -> image signing
 -> staging deployment
 -> forked-chain security tests
 -> shadow policy replay
 -> promotion
```

## 162. GitHub Actions skeleton

A production repository can translate the pipeline into separate least-privilege jobs. Do not expose mainnet RPC or signer credentials to pull-request jobs.

## 163. Kubernetes production topology

```text
Namespace: agentshield

API Deployment
Policy Deployment
Simulation Worker Deployment
Trust Adapter Deployment
Approval Service
Capability Signer
OTel Collector

Managed PostgreSQL
Managed Redis
Event Broker
KMS/HSM
Immutable Archive
```

## 164. Kubernetes security

Add:

```text
NetworkPolicy
PodDisruptionBudget
HorizontalPodAutoscaler
topologySpreadConstraints
seccomp
readOnlyRootFilesystem
drop ALL capabilities
runAsNonRoot
workload identity
admission policy
signed image verification
egress allowlists
```

## 165. Network policy

The API should not need unrestricted Internet access.

Separate egress:

```text
API -> internal services
Simulator -> approved RPC
Trust adapter -> Ethereum RPC/registry metadata
Signer -> KMS only
```

## 166. Secret management

Do not store:

```text
wallet private keys
KMS credentials
mainnet RPC secrets
approval signing keys
database passwords
```

in Git or baked images.

Use workload identity and a managed secret system.

## 167. Observability trace

One trace can span:

```text
POST /analyze
 -> delegation.verify
 -> identity.resolve
 -> provenance.resolve
 -> simulation.run
 -> assetflow.build
 -> policy.evaluate
 -> risk.evaluate
 -> capability.mint
```

Never put secrets or full private prompts into telemetry by default.

## 168. Security metrics

Operational metrics:

```text
ALLOW rate
REVIEW rate
BLOCK rate
simulation failures
simulation disagreement
delegation failures
replay attempts
approval latency
capability mint rate
capability rejection
wallet enforcement failures
receipt reconciliation failures
quarantined agents
```

## 169. Audit metrics

Track:

```text
decisions with complete provenance
decisions with simulation block
executions with receipt
executions matching approved tx hash
policy version coverage
verification freshness
```

## 170. Alert examples

Page immediately for:

```text
wallet executed without decision
capability signer key anomaly
cross-tenant decision access
mass replay attempts
policy admin compromise
simulation disagreement on high-value tx
unexpected contract upgrade
audit-event loss
```

## 171. Performance model

Latency budget example:

```text
auth + request validation        10 ms
delegation/provenance            20 ms
trust cache                      20 ms
simulation                      500-1200 ms
policy/risk                      20 ms
persistence                      20 ms
capability signing               20 ms
```

Simulation dominates.

## 172. Scale strategy

Scale independently:

```text
API workers
simulation workers
trust adapters
policy workers
event consumers
```

Partition event streams by tenant/wallet/session while preserving required ordering.

## 173. Backpressure

If simulation demand exceeds capacity:

```text
queue bounded requests
prioritize high-value/interactive actions
reject beyond safe queue depth
do not skip simulation to reduce latency
```

## 174. Caching

Safe candidates:

```text
ABI
verified contract metadata
finalized ERC-8004 identity snapshot
policy bundles
code hash analysis
```

Unsafe/staleness-sensitive:

```text
balance
allowance
nonce
proxy implementation
verification freshness
transaction simulation
```

## 175. RPC redundancy

Use provider diversity.

For high-value decisions:

```text
RPC A block/hash
RPC B block/hash
Simulator block/hash
```

Disagreement can trigger review/fail closed.

## 176. Reorg handling

Link simulation and execution to block identifiers. If a reorg invalidates assumptions before finality, mark the execution record accordingly and reconcile.

## 177. Proxy upgrade handling

A target allowlist should key on more than address:

```text
proxy address
implementation address
implementation code hash
admin
upgradeability
last checked block
```

## 178. DEX application

For swaps validate:

```text
pair
amount
route
router
recipient
min output
slippage
deadline
approval
price impact
MEV
```

## 179. Lending application

Validate:

```text
protocol
market
collateral
borrow asset
LTV
health factor
interest mode
oracle
liquidation risk
approval
recipient
```

## 180. Staking application

Validate:

```text
validator/protocol
amount
lock/unbonding
derivative token
recipient
slashing assumptions
withdrawal address
```

## 181. Treasury application

Controls:

```text
destination allowlist
daily/weekly limits
multi-person approval
stablecoin policy
bridge policy
accounting reference
business purpose
```

## 182. DAO application

Controls:

```text
proposal id
approved execution bundle
timelock
target contracts
upgrade bytecode
treasury ceiling
governance state
```

## 183. Bridge application

Controls:

```text
source chain
destination chain
canonical bridge
token mapping
recipient
minimum received
message finality
bridge risk
```

## 184. NFT application

Controls:

```text
marketplace
collection
token id
maximum price
recipient
royalty/payment flow
operator approval
```

## 185. Autonomous market-making application

Requires stronger controls:

```text
inventory ceiling
venue allowlist
price bands
loss limits
position limits
oracle quality
emergency stop
```

## 186. Smart-contract engineering agent

If an AI agent deploys/upgrades contracts:

```text
source commit
compiler
bytecode hash
audit status
deployment address
constructor args
proxy implementation
upgrade approval
```

must be bound to authorization.

## 187. Cross-agent application

Example:

```text
Portfolio Agent
  -> Research Agent [read-only]
  -> Risk Agent [read-only]
  -> DeFi Agent [bounded write]
      -> Swap Agent [narrow swap capability]
```

Research agents should not inherit financial authority merely because they contributed context.

## 188. RAG-enabled DeFi agent

```text
Protocol docs
Governance forum
Market data
Token metadata
      |
 provenance labels
      v
Agent reasoning
      |
transaction proposal
      |
AgentShield
```

Retrieved text remains untrusted context.

## 189. Prompt-injection defense in depth

AgentShield should not depend on one prompt-injection classifier.

Use:

```text
content trust labels
task alignment
tool policy
transaction simulation
asset-flow verification
approval limits
wallet enforcement
runtime EDR
```

If the classifier misses an injection but the resulting transaction violates intent, the financial guard can still block it.

## 190. Contract compromise defense

A previously approved router can become unsafe through proxy upgrade or governance compromise. Re-resolve implementation/code hash and security status according to risk/value policy.

## 191. Oracle manipulation

For price-sensitive actions, compare independent price sources and simulation output. A manipulated spot price should not silently redefine the user's intended economic threshold.

## 192. MEV-aware execution

Policy can select:

```text
public mempool
private relay
intent/solver system
```

based on value and sandwich risk, while recording the chosen execution path.

## 193. Compliance extension

Where legally required, add compliance as an independent policy input. Do not mix compliance decisions with agent reputation or model confidence.

## 194. Multi-chain extension

Every chain adapter needs:

```text
chain identity
finality model
transaction decoder
simulator
asset model
wallet enforcement
replay domain
```

Never reuse Ethereum assumptions blindly on another chain.

## 195. L2 extension

For rollups also record:

```text
L2 chain id
sequencer status
L1 origin
withdrawal/finality semantics
bridge path
```

## 196. Security testing strategy

Four layers:

```text
unit invariants
integration/fork tests
property/fuzz tests
adversarial end-to-end scenarios
```

## 197. Required unit tests

Expand current tests to cover:

```text
expired delegation
broken parent digest
wrong final delegatee
wrong router
wrong recipient
value excess
MEV excess
contract risk excess
simulation revert
delegatecall
replay
chain mismatch
stale evidence
```

## 198. Fork tests

Use a fork to exercise real contracts:

```text
Uniswap swap
ERC-20 approval
Permit2
proxy target
multicall
bridge
```

Assertions should inspect actual state diffs.

## 199. Fuzz tests

Fuzz:

```text
delegation depth
capability sets
value ceilings
expiry boundaries
calldata
approval values
nested calls
policy thresholds
```

Property:

```text
no mutation may cause child authority > parent
```

## 200. Adversarial scenarios

Maintain a corpus:

```text
malicious webpage
malicious token metadata
compromised MCP server
malicious router
malicious proxy upgrade
RPC disagreement
approval phishing
wrong recipient
bridge redirection
stale simulation
review substitution
cross-tenant replay
```

## 201. Evaluation metrics

Security:

```text
attack prevention rate
false allow rate
false review rate
false block rate
authority escalation prevention
intent mismatch recall
approval-abuse recall
```

Operations:

```text
p50/p95/p99 latency
simulation throughput
review latency
availability
reconciliation delay
```

## 202. Red-team release gate

A release should not reach financial production until critical attack traces pass and no BLOCK path can mint or execute authority.

## 203. Chaos testing

Inject:

```text
RPC timeout
RPC disagreement
Postgres failover
Redis loss
KMS latency
simulation worker loss
event broker lag
policy service outage
```

Verify conservative degradation.

## 204. Disaster recovery

Define:

```text
RPO
RTO
database backup
audit archive
policy backup
KMS recovery
regional failover
revocation restoration
```

Never restore old revocation state without reconciliation.

## 205. Security review checklist

Before production:

```text
[ ] wallet cannot bypass enforcement
[ ] tenant derived from auth
[ ] signed delegation
[ ] no authority expansion
[ ] simulation complete
[ ] state/asset flow checked
[ ] exact-action approval
[ ] KMS signer
[ ] replay prevention
[ ] revocation
[ ] immutable evidence
[ ] incident runbook
[ ] independent contract audit
[ ] fuzz/invariant tests
[ ] fork tests
[ ] load/chaos tests
```

## 206. Principal-level design trade-off: off-chain vs on-chain policy

On-chain advantages:

```text
strong final enforcement
public auditability
less reliance on backend
```

Costs:

```text
gas
policy complexity
privacy
upgrade friction
limited external context
```

Recommended split:

```text
rich analysis off-chain
+
compact cryptographic commitment
+
critical invariant enforcement on-chain
```

## 207. Principal-level trade-off: score vs rules

Risk scores help prioritize ambiguous evidence. Rules enforce invariants.

Never encode:

```text
risk < 20 => bypass all rules
```

Instead:

```text
hard rules first
risk/review second
```

## 208. Principal-level trade-off: one simulator vs quorum

One simulator is cheaper and faster.

Multiple independent simulators reduce correlated failure/manipulation for high-value actions.

Use value-tiered policy.

## 209. Principal-level trade-off: monolith vs microservices

Begin with a modular monolith for policy correctness and atomic reasoning. Split simulation, signing, trust adapters and event processing where isolation, scale or ownership justify it.

## 210. Principal-level trade-off: synchronous vs event-driven

The authorization hot path is synchronous.

Audit, analytics, SOC, model evaluation and long-running reconciliation should be event driven.

## 211. Principal-level trade-off: model intelligence vs deterministic safety

Use models for:

```text
intent extraction
classification
investigation
explanation
```

Use deterministic mechanisms for:

```text
identity
delegation
value limits
target policy
hash binding
replay
wallet enforcement
```

## 212. Failure-mode matrix

| Failure | Safe behavior |
|---|---|
| Agent unavailable | No new proposal |
| Trust adapter unavailable | Review/block according to policy |
| Simulator unavailable | Block financial execution |
| Policy unavailable | Fail closed |
| KMS unavailable | No capability mint |
| Approval service unavailable | No reviewed execution |
| PostgreSQL unavailable | Do not execute if audit durability required |
| Redis unavailable | Fall back only if replay guarantees remain safe |
| RPC disagreement | Review/block |
| Wallet PEP unavailable | No execution |

## 213. Production maturity levels

### Level 0 — Demo
Local API, sample simulation evidence, local DB.

### Level 1 — Controlled testnet
Real RPC, fork simulation, signed delegation, test smart account.

### Level 2 — Limited mainnet
Low-value caps, KMS, SSO review, audited wallet, live monitoring.

### Level 3 — Enterprise
HA, immutable evidence, SIEM, policy lifecycle, revocation, multi-region, formal/fuzz/fork gates.

### Level 4 — High-value autonomous finance
Strict value tiers, independent simulation, multi-person approval, hardened custody architecture, continuous red-team and incident response.

## 214. Example explanation

A concise system-design explanation:

> AgentShield separates probabilistic planning from deterministic financial authority. The agent proposes an intent and transaction, but an independent runtime reconstructs identity and attenuated delegation, tracks provenance, simulates the exact Ethereum action, extracts state and asset-flow effects, compares those effects against compiled user intent, applies hard policy plus risk, and only then issues a short-lived exact-action capability. The wallet is the final enforcement point, while the Flight Recorder preserves the causal path from user goal to on-chain receipt.

## 215. Why this is not merely another wallet firewall

A wallet firewall sees a transaction.

AgentShield sees:

```text
user goal
+
agent identity
+
agent verification/reputation
+
multi-agent delegation
+
retrieval/tool provenance
+
transaction
+
simulated effects
+
behavioral history
```

That extra causal and authority context is what makes it an **agent security runtime**.

## 216. Recommended extension roadmap

### Milestone A — cryptographic authority
- EIP-712 delegation signatures
- asymmetric capability signer
- nonce/revocation store

### Milestone B — Ethereum semantics
- ABI resolver
- trace parser
- state-diff extractor
- complete asset-flow graph
- proxy awareness

### Milestone C — standards integration
- ERC-8004 adapter
- ERC-8126 adapter
- canonical ERC-8196 module
- ERC-4337 bundler/account PEP

### Milestone D — enterprise operations
- OIDC/workload identity
- SSO approvals
- OTel
- SIEM
- Alembic
- outbox/event bus
- immutable evidence

### Milestone E — autonomous security
- behavioral EDR
- quarantine
- SOC investigator
- historical replay
- counterfactual policy simulation

## 217. Final architecture summary

```text
                         USER
                          |
                          v
                    Financial Goal
                          |
                          v
                       AI Agent
                          |
                  Structured Intent
                          |
                  Proposed Transaction
                          |
                          v
+----------------------------------------------------------------+
|                         AGENTSHIELD                            |
|                                                                |
| Identity ---- ERC-8004                                         |
| Verification - ERC-8126                                        |
| Reputation                                                     |
| Delegation ---- cryptographic attenuation                       |
| Provenance ---- causal trust graph                              |
| Intent -------- deterministic invariants                        |
| Simulation ---- call tree + state diff                          |
| Asset Flow ---- economic effects                               |
| Risk ---------- contract + MEV + behavior                       |
| Policy -------- hard gates + autonomy tier                      |
| Approval ------ exact-action HITL                               |
| Capability ---- short-lived / single-use                        |
+-------------------------------+--------------------------------+
                                |
                ALLOW / REVIEW / BLOCK
                                |
                                v
+----------------------------------------------------------------+
|                  EXECUTION ENFORCEMENT                         |
| ERC-8196 policy-bound wallet + ERC-4337 smart account          |
+-------------------------------+--------------------------------+
                                |
                                v
                            ETHEREUM
                                |
                                v
+----------------------------------------------------------------+
|                       FLIGHT RECORDER                          |
| goal -> context -> delegation -> tx -> simulation -> decision  |
| -> approval -> UserOperation -> receipt -> post-state          |
+-------------------------------+--------------------------------+
                                |
                                v
                       AGENT EDR / SOC
```

## 218. Canonical public references

- ERC-8196 — AI Agent Authenticated Wallet: https://eips.ethereum.org/EIPS/eip-8196
- ERC-8004 — Trustless Agents: https://eips.ethereum.org/EIPS/eip-8004
- ERC-8126 — AI Agent Verification: https://eips.ethereum.org/EIPS/eip-8126
- ERC-4337 — Account Abstraction Using Alt Mempool: https://eips.ethereum.org/EIPS/eip-4337

These standards provide public interoperability context. The AgentShield architecture and implementation in this repository are independent reference engineering and do not claim to reproduce any private Ethereum Foundation, wallet vendor, protocol, or agent implementation.

## 219. Closing principle

```text
THE MODEL MAY CHOOSE WHAT TO PROPOSE.
THE OWNER'S POLICY CHOOSES WHAT MAY EXECUTE.

Trust the agent enough to plan.
Never trust it enough to self-authorize.
```
