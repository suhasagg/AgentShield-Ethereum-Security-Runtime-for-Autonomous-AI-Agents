# Operations Runbook

## Health
`GET /health`

## Safe degradation
If simulation, identity verification, signer, or policy service is unhealthy:
- block autonomous financial writes;
- retain read-only analysis where safe;
- page on-call;
- preserve pending requests for reconciliation.

## Critical incident
1. Revoke agent/session.
2. Disable wallet execution path.
3. Revoke JIT capability signer keys if compromised.
4. Preserve flight recorder.
5. Inspect pending UserOperations.
6. Reconcile receipts/nonces.
7. Rotate exposed credentials.
8. Patch policy/detector.
9. Replay historical proposals.
10. Require human recovery approval.
