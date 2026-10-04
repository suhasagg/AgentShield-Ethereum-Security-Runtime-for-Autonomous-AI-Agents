from .domain import TransactionIntent, ProposedTransaction, SimulationResult

def compare(intent: TransactionIntent, tx: ProposedTransaction, sim: SimulationResult):
    reasons = []
    if intent.approved_routers and tx.target.lower() not in {x.lower() for x in intent.approved_routers}:
        reasons.append("TARGET_NOT_APPROVED_ROUTER")
    if intent.amount_in is not None and tx.value > intent.amount_in:
        reasons.append("VALUE_EXCEEDS_INTENDED_AMOUNT")
    if intent.recipient:
        recipients = {f.recipient.lower() for f in sim.asset_flows}
        if recipients and intent.recipient.lower() not in recipients:
            reasons.append("ASSET_FLOW_RECIPIENT_MISMATCH")
    if intent.forbid_delegatecall and sim.uses_delegatecall:
        reasons.append("DELEGATECALL_FORBIDDEN")
    if intent.max_new_approval is not None:
        for approval in sim.state_diff.approvals:
            amount = int(approval.get("amount", 0))
            if amount > intent.max_new_approval:
                reasons.append("TOKEN_APPROVAL_EXCEEDS_INTENT")
                break
    if sim.mev_risk > intent.max_mev_risk:
        reasons.append("MEV_RISK_EXCEEDS_THRESHOLD")
    if sim.contract_risk > intent.max_contract_risk:
        reasons.append("CONTRACT_RISK_EXCEEDS_THRESHOLD")
    if not sim.success:
        reasons.append("SIMULATION_REVERTED")
    if sim.decoded_action and intent.action.lower() not in sim.decoded_action.lower():
        reasons.append("DECODED_ACTION_MISMATCH")
    return reasons
