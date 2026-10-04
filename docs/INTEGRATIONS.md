# Integration Guide

## ERC-8004
Read agent identity, reputation and validation signals. Cache only with block/finality metadata.

## ERC-8126
Retrieve verification/risk evidence and enforce freshness. Lower risk score is safer per the public ERC.

## ERC-8196
Use the canonical wallet/module interface for policy-bound agent execution. AgentShield's action envelope is an integration seam, not a substitute for canonical validation.

## ERC-4337
Gate UserOperation construction/submission and enforce again in the smart account.

## Simulation
Implement the `Simulator` interface with Anvil/reth/Erigon/commercial simulation. Return full internal calls, state diff, approvals and asset flows.

## Agent EDR
Feed retrieval/tool/memory provenance and receive quarantine state. A quarantined agent should not obtain a capability token.
