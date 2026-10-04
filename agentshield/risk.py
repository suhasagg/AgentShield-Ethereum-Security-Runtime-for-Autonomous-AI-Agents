def score(*, intent_reasons: list[str], delegation_reasons: list[str], untrusted: bool,
          side_effect: bool, reputation: int, sim_mev: int, sim_contract: int):
    value = 0
    value += min(45, 15 * len(intent_reasons))
    value += min(60, 30 * len(delegation_reasons))
    if untrusted and side_effect:
        value += 25
    if reputation < 20:
        value += 15
    value += min(20, sim_mev // 5)
    value += min(20, sim_contract // 5)
    return min(100, value)
