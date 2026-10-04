from __future__ import annotations
from abc import ABC, abstractmethod
from .domain import ProposedTransaction, SimulationResult

class Simulator(ABC):
    @abstractmethod
    async def simulate(self, tx: ProposedTransaction) -> SimulationResult: ...

class DeterministicSimulator(Simulator):
    """Safe local adapter for tests/demos. Production should plug in a forked-EVM simulator."""
    async def simulate(self, tx: ProposedTransaction) -> SimulationResult:
        return SimulationResult(success=True, decoded_action="unknown")

class JsonRpcSimulator(Simulator):
    """
    Production integration seam.

    A real deployment should call a dedicated simulation service/fork and return:
    decoded calldata, internal calls, logs, state diff, approvals, asset flows and
    delegatecall evidence. eth_call alone is not sufficient for complete state-diff analysis.
    """
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    async def simulate(self, tx: ProposedTransaction) -> SimulationResult:
        raise NotImplementedError("Connect Tenderly/Anvil/reth/Erigon trace adapter in deployment.")
