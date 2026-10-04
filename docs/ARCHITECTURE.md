# Architecture

AgentShield is split into a probabilistic planning domain and deterministic execution domain.

```text
AI / planner -> structured proposal -> AgentShield -> wallet PEP -> Ethereum
```

The security boundary is complete only when the wallet/bundler refuses execution without a valid AgentShield/canonical policy proof. Off-chain analysis alone is advisory.

## Control-plane components

- Identity adapter: ERC-8004 and enterprise workload identity.
- Verification adapter: ERC-8126 and other trust evidence.
- Delegation verifier: non-expanding authority.
- Provenance service: causal input lineage.
- Intent compiler: natural language to typed invariants.
- Simulator: forked EVM plus call/state traces.
- Asset-flow engine: economic effects.
- Policy/risk engine: deterministic gates and review thresholds.
- Capability signer: exact-action JIT authority.
- Flight recorder: causal evidence.
- Wallet enforcement: ERC-8196/4337 integration.

## Data plane

The transaction path must remain short and fail closed. Expensive analytics can run before the final deterministic gate; the final wallet check should verify compact commitments/proofs.
