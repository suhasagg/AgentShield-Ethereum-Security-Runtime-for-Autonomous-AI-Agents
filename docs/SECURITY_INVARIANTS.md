# Security Invariants

1. Model output is a proposal, not authority.
2. Identity is not authorization.
3. Reputation never overrides a hard policy.
4. Child authority is a subset of parent authority.
5. Untrusted provenance cannot create permission.
6. ALLOW requires simulation evidence.
7. BLOCK never mints an execution capability.
8. Human approval binds the exact transaction.
9. Changing calldata invalidates the action digest.
10. Critical enforcement lives outside the agent process.
11. Evidence is append-only/tamper-evident in production.
12. The wallet is the final financial enforcement point.
