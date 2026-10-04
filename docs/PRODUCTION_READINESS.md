# Production Readiness

The repository is a runnable security core, not a turnkey custody product.

Before mainnet value:
1. Integrate enterprise OIDC/workload identity.
2. Replace unsigned delegation examples with EIP-712 signed credentials.
3. Integrate live ERC-8004 and ERC-8126 reads with freshness/finality.
4. Deploy a real forked-EVM simulation cluster and complete call/state/asset-flow analysis.
5. Integrate canonical ERC-8196 and ERC-4337 wallet enforcement.
6. Move capability signing to KMS/HSM.
7. Implement nonce/revocation and exact-action consumption.
8. Add SSO approvals, separation of duties and value-tier policies.
9. Add Alembic migrations, HA Postgres/Redis, event outbox and immutable audit archive.
10. Add OTel/Prometheus/SIEM.
11. Run fork, fuzz, invariant, formal, load and adversarial tests.
12. Obtain independent smart-contract/security review before real custody.
