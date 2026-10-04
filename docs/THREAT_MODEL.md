# Threat Model

## Assets
Owner funds, approvals, wallet authority, delegation credentials, policy bundles, signer keys, simulation integrity, audit evidence.

## Adversaries
Prompt-injection author, malicious dApp/router, compromised agent runtime, malicious sub-agent, malicious RPC, insider policy admin, stolen credential holder.

## Required properties
- Child delegation cannot expand parent authority.
- Untrusted content cannot create permission.
- Transaction effects must match intent.
- Review binds the exact transaction.
- Replay is rejected.
- High-value execution fails closed when critical evidence is unavailable.
- Agent cannot modify its own policy or erase evidence.
